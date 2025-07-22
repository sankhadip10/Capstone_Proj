from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, datetime
import logging

from .models import Order, Product, Customer, OrderItem
from core.models import User

logger = logging.getLogger(__name__)


# =============================================================================
# ORDER PROCESSING TASKS
# =============================================================================

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    """
    Send order confirmation email to customer
    Retries up to 3 times with exponential backoff
    """
    try:
        order = Order.objects.select_related('customer__user').prefetch_related(
            'items__product'
        ).get(id=order_id)

        customer = order.customer
        user = customer.user

        # Calculate order total and prepare items with totals
        order_items_with_totals = []
        order_total = 0

        for item in order.items.all():
            item_total = item.quantity * item.unit_price
            order_total += item_total

            # Add item_total to the item for template
            item.item_total = item_total
            order_items_with_totals.append(item)

        # Email context
        context = {
            'customer_name': f"{user.first_name} {user.last_name}",
            'order': order,
            'order_total': order_total,
            'order_items': order_items_with_totals,
            'company_name': 'Django Storefront',
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }

        # Render email templates
        subject = f'Order Confirmation #{order.id}'
        text_content = render_to_string('emails/order_confirmation.txt', context)
        html_content = render_to_string('emails/order_confirmation.html', context)

        # Send email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Order confirmation email sent for order {order_id}")
        return f"Email sent successfully for order {order_id}"

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Failed to send order confirmation for {order_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task
def update_inventory_after_order(order_id):
    """
    Update product inventory levels after order placement
    """
    try:
        with transaction.atomic():
            order = Order.objects.prefetch_related('items__product').get(id=order_id)

            for item in order.items.all():
                product = item.product
                if product.inventory >= item.quantity:
                    product.inventory -= item.quantity
                    product.save(update_fields=['inventory'])
                    logger.info(f"Updated inventory for product {product.id}: -{item.quantity}")
                else:
                    logger.warning(f"Insufficient inventory for product {product.id}")

        return f"Inventory updated for order {order_id}"

    except Exception as exc:
        logger.error(f"Failed to update inventory for order {order_id}: {exc}")
        raise


@shared_task
def send_low_inventory_alert(product_id, current_stock):
    """
    Send low inventory alert to admin
    """
    try:
        product = Product.objects.get(id=product_id)

        # Send to admin users
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)

        subject = f'Low Inventory Alert: {product.title}'
        message = f'''
        Product: {product.title}
        Current Stock: {current_stock}
        Product ID: {product_id}

        Please restock this item soon.
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(admin_emails),
            fail_silently=False
        )

        logger.info(f"Low inventory alert sent for product {product_id}")
        return f"Low inventory alert sent for product {product_id}"

    except Exception as exc:
        logger.error(f"Failed to send low inventory alert for product {product_id}: {exc}")
        raise


# =============================================================================
# ANALYTICS AND REPORTING TASKS
# =============================================================================

@shared_task
def generate_daily_sales_report():
    """
    Generate daily sales report for admin
    """
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Get yesterday's orders
        orders = Order.objects.filter(
            placed_at__date=yesterday,
            payment_status=Order.PAYMENT_STATUS_COMPLETE
        ).prefetch_related('items__product')

        total_orders = orders.count()
        total_revenue = sum(
            sum(item.quantity * item.unit_price for item in order.items.all())
            for order in orders
        )

        # Top selling products
        product_sales = {}
        for order in orders:
            for item in order.items.all():
                if item.product.id not in product_sales:
                    product_sales[item.product.id] = {
                        'name': item.product.title,
                        'quantity': 0,
                        'revenue': 0
                    }
                product_sales[item.product.id]['quantity'] += item.quantity
                product_sales[item.product.id]['revenue'] += item.quantity * item.unit_price

        # Sort by revenue
        top_products = sorted(
            product_sales.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )[:5]

        # Send report to admin
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)

        subject = f'Daily Sales Report - {yesterday.strftime("%B %d, %Y")}'

        context = {
            'date': yesterday.strftime('%B %d, %Y'),
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'top_products': top_products,
        }

        text_content = render_to_string('emails/daily_sales_report.txt', context)
        html_content = render_to_string('emails/daily_sales_report.html', context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(admin_emails)
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Daily sales report generated for {yesterday}")
        return f"Daily sales report generated: {total_orders} orders, ${total_revenue}"

    except Exception as exc:
        logger.error(f"Failed to generate daily sales report: {exc}")
        raise


@shared_task
def cleanup_abandoned_carts():
    """
    Clean up abandoned carts older than 7 days
    """
    try:
        from .models import Cart

        cutoff_date = timezone.now() - timedelta(days=7)
        abandoned_carts = Cart.objects.filter(created_at__lt=cutoff_date)

        count = abandoned_carts.count()
        abandoned_carts.delete()

        logger.info(f"Cleaned up {count} abandoned carts")
        return f"Cleaned up {count} abandoned carts"

    except Exception as exc:
        logger.error(f"Failed to cleanup abandoned carts: {exc}")
        raise


@shared_task
def check_inventory_levels():
    """
    Check all products for low inventory and send alerts
    """
    try:
        LOW_STOCK_THRESHOLD = 10

        low_stock_products = Product.objects.filter(inventory__lte=LOW_STOCK_THRESHOLD)

        for product in low_stock_products:
            send_low_inventory_alert.delay(product.id, product.inventory)

        logger.info(f"Checked inventory levels: {low_stock_products.count()} products low")
        return f"Inventory check complete: {low_stock_products.count()} low stock alerts sent"

    except Exception as exc:
        logger.error(f"Failed to check inventory levels: {exc}")
        raise


@shared_task
def process_payment_webhook(webhook_event_id):
    """
    Process Razorpay webhook events
    """
    try:
        from payments.models import WebhookEvent, PaymentIntent

        webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
        event_data = webhook_event.data

        event_type = event_data.get('event')
        payment_data = event_data.get('payload', {}).get('payment', {}).get('entity', {})

        logger.info(f"Processing webhook event: {event_type}")
        logger.info(f"Payment data: {payment_data}")

        if event_type == 'payment.captured':
            # Find payment intent
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')

            logger.info(f"Looking for PaymentIntent with razorpay_order_id: {order_id}")

            try:
                payment_intent = PaymentIntent.objects.get(razorpay_order_id=order_id)
                logger.info(f"Found PaymentIntent: {payment_intent.id}")

                with transaction.atomic():
                    # Update payment intent
                    payment_intent.razorpay_payment_id = payment_id
                    payment_intent.status = 'paid'
                    payment_intent.webhook_received = True
                    payment_intent.webhook_data = event_data
                    payment_intent.save()

                    # Update order using YOUR existing model structure
                    order = payment_intent.order
                    order.payment_status = Order.PAYMENT_STATUS_COMPLETE
                    order.save()

                    # Link webhook event
                    webhook_event.payment_intent = payment_intent
                    webhook_event.processed = True
                    webhook_event.save()

                    # Trigger fulfillment
                    prepare_order_fulfillment.delay(order.id)

                logger.info(f"Payment webhook processed successfully: {payment_id}")

            except PaymentIntent.DoesNotExist:
                logger.error(f"PaymentIntent not found for order_id: {order_id}")

                # List all available PaymentIntents for debugging
                available_intents = PaymentIntent.objects.all().values_list('razorpay_order_id', flat=True)
                logger.error(f"Available PaymentIntents: {list(available_intents)}")

                # Mark webhook as processed even if PaymentIntent not found
                webhook_event.processed = True
                webhook_event.save()

        elif event_type == 'payment.failed':
            # Handle failed payments
            order_id = payment_data.get('order_id')

            try:
                payment_intent = PaymentIntent.objects.get(razorpay_order_id=order_id)
                payment_intent.status = 'failed'
                payment_intent.save()

                # Update order
                order = payment_intent.order
                order.payment_status = Order.PAYMENT_STATUS_FAILED
                order.save()

                logger.info(f"Payment failed for order: {order.id}")

            except PaymentIntent.DoesNotExist:
                logger.error(f"PaymentIntent not found for failed payment: {order_id}")

        return f"Webhook {event_type} processed successfully"

    except Exception as exc:
        logger.error(f"Failed to process webhook {webhook_event_id}: {exc}")
        # Don't re-raise to prevent infinite retries
        return f"Webhook processing failed: {exc}"

@shared_task
def prepare_order_fulfillment(order_id):
    """
    Prepare order for fulfillment after successful payment
    """
    try:
        order = Order.objects.get(id=order_id)

        # Here you would integrate with shipping providers, warehouse systems, etc.
        logger.info(f"Preparing fulfillment for order {order_id}")

        # Send fulfillment notification
        send_fulfillment_notification.delay(order_id)

        return f"Fulfillment preparation started for order {order_id}"

    except Exception as exc:
        logger.error(f"Failed to prepare fulfillment for order {order_id}: {exc}")
        raise


@shared_task
def send_fulfillment_notification(order_id):
    """
    Send shipping notification to customer
    """
    try:
        order = Order.objects.select_related('customer__user').get(id=order_id)
        customer = order.customer
        user = customer.user

        context = {
            'customer_name': f"{user.first_name} {user.last_name}",
            'order': order,
            'tracking_number': f"TRK{order_id:06d}",  # Mock tracking number
        }

        subject = f'Your Order #{order.id} Has Shipped!'

        # For now, just send a simple email (you can create templates later)
        message = f'''
        Dear {context['customer_name']},

        Great news! Your order #{order.id} has been shipped and is on its way to you.

        Tracking Number: {context['tracking_number']}
        Estimated Delivery: 3-5 business days

        Thank you for shopping with Django Storefront!
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        logger.info(f"Shipping notification sent for order {order_id}")
        return f"Shipping notification sent for order {order_id}"

    except Exception as exc:
        logger.error(f"Failed to send shipping notification for order {order_id}: {exc}")
        raise


@shared_task
def process_payment_webhook(webhook_event_id):
    """
    Process Razorpay webhook events
    """
    try:
        from payments.models import WebhookEvent, PaymentIntent

        webhook_event = WebhookEvent.objects.get(id=webhook_event_id)
        event_data = webhook_event.data

        event_type = event_data.get('event')
        payment_data = event_data.get('payload', {}).get('payment', {}).get('entity', {})

        if event_type == 'payment.captured':
            # Find payment intent
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')

            try:
                payment_intent = PaymentIntent.objects.get(razorpay_order_id=order_id)

                with transaction.atomic():
                    # Update payment intent
                    payment_intent.razorpay_payment_id = payment_id
                    payment_intent.status = 'paid'
                    payment_intent.webhook_received = True
                    payment_intent.webhook_data = event_data
                    payment_intent.save()

                    # Update order using YOUR existing model structure
                    order = payment_intent.order
                    order.payment_status = Order.PAYMENT_STATUS_COMPLETE  # Uses your existing constants
                    order.save()

                    # Link webhook event
                    webhook_event.payment_intent = payment_intent
                    webhook_event.processed = True
                    webhook_event.save()

                    # Trigger fulfillment
                    prepare_order_fulfillment.delay(order.id)

                logger.info(f"Payment webhook processed: {payment_id}")

            except PaymentIntent.DoesNotExist:
                logger.error(f"PaymentIntent not found for order_id: {order_id}")

        elif event_type == 'payment.failed':
            # Handle failed payments using YOUR existing model structure
            order_id = payment_data.get('order_id')

            try:
                payment_intent = PaymentIntent.objects.get(razorpay_order_id=order_id)
                payment_intent.status = 'failed'
                payment_intent.save()

                # Update order
                order = payment_intent.order
                order.payment_status = Order.PAYMENT_STATUS_FAILED  # Uses your existing constants
                order.save()

                logger.info(f"Payment failed for order: {order.id}")

            except PaymentIntent.DoesNotExist:
                logger.error(f"PaymentIntent not found for failed payment: {order_id}")

        return f"Webhook {event_type} processed successfully"

    except Exception as exc:
        logger.error(f"Failed to process webhook {webhook_event_id}: {exc}")
        raise
