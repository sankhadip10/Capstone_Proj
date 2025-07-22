import pytest
from unittest.mock import patch
from django.db.models.signals import post_save
from model_bakery import baker

from core.models import User
from store.models import Customer, Product, Order
from store.signals import order_created


@pytest.mark.django_db
class TestSignals:

    def test_customer_created_on_user_creation(self):
        """Test that customer is auto-created when user is created"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        assert Customer.objects.filter(user=user).exists()
        customer = Customer.objects.get(user=user)
        assert customer.membership == Customer.MEMBERSHIP_BRONZE

    @patch('store.tasks.send_order_confirmation_email.delay')
    @patch('store.tasks.update_inventory_after_order.delay')
    def test_order_created_signal(self, mock_update_inventory, mock_send_email):
        """Test that order creation triggers background tasks"""
        user = baker.make(User)
        customer = baker.make(Customer, user=user)
        order = baker.make(Order, customer=customer)

        # Manually send signal (since it's triggered in serializer)
        order_created.send(sender=Order, order=order)

        mock_send_email.assert_called_once_with(order.id)
        mock_update_inventory.assert_called_once_with(order.id)

    @patch('store.tasks.send_low_inventory_alert.delay')
    def test_low_inventory_signal(self, mock_send_alert):
        """Test that low inventory triggers alert"""
        product = baker.make(Product, inventory=50)

        # Update inventory to low level
        product.inventory = 5
        product.save()

        mock_send_alert.assert_called_once_with(product.id, 5)