import pytest
from unittest.mock import patch, MagicMock
from django.core import mail
from django.test import override_settings
from model_bakery import baker

from store.tasks import (
    send_order_confirmation_email,
    update_inventory_after_order,
    send_low_inventory_alert,
    generate_daily_sales_report,
    cleanup_abandoned_carts
)
from store.models import Order, Product, Customer, Cart
from core.models import User


@pytest.mark.django_db
class TestCeleryTasks:

    @pytest.fixture
    def order_with_items(self):
        """Create order with items for testing"""
        user = baker.make(User, email='test@example.com', first_name='Test', last_name='User')
        customer = baker.make(Customer, user=user)
        order = baker.make(Order, customer=customer, payment_status=Order.PAYMENT_STATUS_COMPLETE)

        product = baker.make(Product, title='Test Product', unit_price=Decimal('15.00'))
        baker.make(OrderItem, order=order, product=product, quantity=2, unit_price=product.unit_price)

        return order

    def test_send_order_confirmation_email(self, order_with_items):
        """Test order confirmation email task"""
        # Clear any existing mail
        mail.outbox = []

        result = send_order_confirmation_email(order_with_items.id)

        assert 'Email sent successfully' in result
        assert len(mail.outbox) == 1

        email = mail.outbox[0]
        assert f'Order Confirmation #{order_with_items.id}' in email.subject
        assert 'test@example.com' in email.to
        assert 'Test User' in email.body

    def test_update_inventory_after_order(self, order_with_items):
        """Test inventory update task"""
        order_item = order_with_items.items.first()
        product = order_item.product
        original_inventory = product.inventory

        result = update_inventory_after_order(order_with_items.id)

        product.refresh_from_db()
        assert product.inventory == original_inventory - order_item.quantity
        assert f'Inventory updated for order {order_with_items.id}' in result

    def test_send_low_inventory_alert(self):
        """Test low inventory alert task"""
        user = baker.make(User, email='admin@example.com', is_staff=True)
        product = baker.make(Product, title='Low Stock Product', inventory=5)

        mail.outbox = []

        result = send_low_inventory_alert(product.id, product.inventory)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert 'Low Inventory Alert' in email.subject
        assert 'Low Stock Product' in email.body
        assert 'admin@example.com' in email.to

    def test_cleanup_abandoned_carts(self):
        """Test abandoned cart cleanup task"""
        from datetime import timedelta
        from django.utils import timezone

        # Create old cart
        old_cart = baker.make(Cart)
        old_cart.created_at = timezone.now() - timedelta(days=8)
        old_cart.save()

        # Create recent cart
        recent_cart = baker.make(Cart)

        result = cleanup_abandoned_carts()

        assert not Cart.objects.filter(id=old_cart.id).exists()
        assert Cart.objects.filter(id=recent_cart.id).exists()
        assert 'Cleaned up 1 abandoned carts' in result

    @patch('store.tasks.timezone')
    def test_generate_daily_sales_report(self, mock_timezone):
        """Test daily sales report generation"""
        from datetime import datetime, date

        # Mock yesterday's date
        mock_timezone.now.return_value.date.return_value = date(2025, 7, 23)

        # Create order from yesterday
        user = baker.make(User, email='admin@example.com', is_staff=True)
        customer = baker.make(Customer, user=user)
        order = baker.make(Order,
                           customer=customer,
                           payment_status=Order.PAYMENT_STATUS_COMPLETE,
                           placed_at=datetime(2025, 7, 22))

        product = baker.make(Product, title='Daily Report Product')
        baker.make(OrderItem, order=order, product=product, quantity=1, unit_price=Decimal('25.00'))

        mail.outbox = []

        result = generate_daily_sales_report()

        assert 'Daily sales report generated' in result
        assert len(mail.outbox) == 1