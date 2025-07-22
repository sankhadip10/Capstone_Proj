import pytest
from unittest.mock import patch, Mock
from decimal import Decimal
from django.core import mail
from model_bakery import baker
from django.contrib.auth import get_user_model

# Import your actual tasks
from store.tasks import (
    send_order_confirmation_email,
    update_inventory_after_order,
    send_low_inventory_alert
)
from store.models import Order, OrderItem, Product, Customer, Collection

User = get_user_model()  # FIXED: Added missing import


@pytest.mark.django_db
class TestCeleryTasks:

    def test_send_order_confirmation_email_task(self):
        """Test order confirmation email task"""
        # Create complete order with items
        user = baker.make(User, email='test@example.com', first_name='Test', last_name='User')
        customer = baker.make(Customer, user=user)
        order = baker.make(Order, customer=customer, payment_status=Order.PAYMENT_STATUS_COMPLETE)

        collection = baker.make(Collection)
        product = baker.make(Product, title='Test Product', unit_price=Decimal('15.00'), collection=collection)
        baker.make(OrderItem, order=order, product=product, quantity=2, unit_price=product.unit_price)

        # Clear mail outbox
        mail.outbox = []

        # Run task
        result = send_order_confirmation_email(order.id)

        # Check result
        assert 'Email sent successfully' in result
        assert len(mail.outbox) == 1

        # Check email content
        email = mail.outbox[0]
        assert f'Order Confirmation #{order.id}' in email.subject
        assert user.email in email.to

    def test_update_inventory_after_order_task(self):
        """Test inventory update task"""
        # Create order with items
        user = baker.make(User)
        customer = baker.make(Customer, user=user)
        order = baker.make(Order, customer=customer)

        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection, inventory=100)
        order_item = baker.make(OrderItem, order=order, product=product, quantity=5, unit_price=product.unit_price)

        original_inventory = product.inventory

        # Run task
        result = update_inventory_after_order(order.id)

        # Check result
        assert f'Inventory updated for order {order.id}' in result

        # Check inventory was updated
        product.refresh_from_db()
        assert product.inventory == original_inventory - order_item.quantity

    def test_send_low_inventory_alert_task(self):
        """Test low inventory alert task"""
        # Create admin user
        admin_user = baker.make(User, email='admin@example.com', is_staff=True)
        collection = baker.make(Collection)
        product = baker.make(Product, title='Low Stock Product', inventory=5, collection=collection)

        # Clear mail outbox
        mail.outbox = []

        # Run task
        result = send_low_inventory_alert(product.id, 5)

        # Check result
        assert f'Low inventory alert sent for product {product.id}' in result
        assert len(mail.outbox) == 1

        # Check email
        email = mail.outbox[0]
        assert 'Low Inventory Alert' in email.subject
        assert product.title in email.body