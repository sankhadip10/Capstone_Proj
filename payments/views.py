from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
import json
import hmac
import hashlib

from .models import PaymentIntent, WebhookEvent
from .serializers import CreatePaymentIntentSerializer, PaymentIntentSerializer, VerifyPaymentSerializer
from .services import RazorpayService
from store.models import Order
from store.tasks import process_payment_webhook


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_intent = serializer.save()

        response_data = {
            'payment_intent': PaymentIntentSerializer(payment_intent).data,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': payment_intent.razorpay_order_id,
            'amount': int(payment_intent.amount * 100),  # Convert to paise
            'currency': payment_intent.currency,
            'name': 'Django Storefront',
            'description': f'Payment for Order #{payment_intent.order.id}',
            'customer': {
                'name': f"{payment_intent.order.customer.user.first_name} {payment_intent.order.customer.user.last_name}",
                'email': payment_intent.order.customer.user.email,
                'contact': payment_intent.order.customer.phone or ''
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_intent = serializer.validated_data['payment_intent']

        with transaction.atomic():
            # Update payment intent
            payment_intent.razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
            payment_intent.status = 'paid'
            payment_intent.save()

            # Update order using YOUR existing constants
            order = payment_intent.order
            order.payment_status = Order.PAYMENT_STATUS_COMPLETE  # Perfect match!
            order.save()

            # Import here to avoid circular imports
            from store.tasks import prepare_order_fulfillment
            prepare_order_fulfillment.delay(order.id)

        return Response({
            'message': 'Payment verified successfully',
            'payment_intent': PaymentIntentSerializer(payment_intent).data,
            'order_status': order.get_payment_status_display()
        })


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    permission_classes = []  # No auth for webhooks

    def post(self, request):
        try:
            # Check if webhook secret is configured
            webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', None)
            if not webhook_secret:
                # For development, skip signature verification
                webhook_data = json.loads(request.body)
                self._process_webhook_data(webhook_data)
                return Response({'status': 'ok (dev mode - no signature check)'})

            # Verify webhook signature (only if secret is configured)
            webhook_signature = request.headers.get('X-Razorpay-Signature')
            webhook_body = request.body

            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                webhook_body,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(webhook_signature or '', expected_signature):
                return Response({'error': 'Invalid signature'}, status=400)

            # Process webhook
            webhook_data = json.loads(webhook_body)
            self._process_webhook_data(webhook_data)

            return Response({'status': 'ok'})

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def _process_webhook_data(self, webhook_data):
        """Process webhook data"""
        event_type = webhook_data.get('event')

        # Store webhook event
        from .models import WebhookEvent
        webhook_event = WebhookEvent.objects.create(
            event_id=webhook_data.get('payload', {}).get('payment', {}).get('entity', {}).get('id', ''),
            event_type=event_type,
            data=webhook_data
        )

        # Process asynchronously
        from store.tasks import process_payment_webhook
        process_payment_webhook.delay(webhook_event.id)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer__user=request.user)
            payment_intents = PaymentIntent.objects.filter(order=order)

            return Response({
                'order_id': order.id,
                'payment_status': order.payment_status,
                'payment_intents': PaymentIntentSerializer(payment_intents, many=True).data
            })

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)