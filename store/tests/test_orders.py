import pytest
from decimal import Decimal
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

from store.models import Order, OrderItem, Product, Customer, Cart, CartItem, Collection

User = get_user_model()


@pytest.mark.django_db
class TestOrderCreation:
    def test_create_order_from_cart(self, api_client, authenticated_user, cart_with_items):
        """Test creating order from cart"""
        response = api_client.post('/store/orders/', {
            'cart_id': str(cart_with_items.id)
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1

        order = Order.objects.first()
        assert order.customer.user == authenticated_user
        assert order.payment_status == Order.PAYMENT_STATUS_PENDING

    def test_order_creates_order_items(self, api_client, authenticated_user, cart_with_items):
        """Test that order items are created with correct prices"""
        response = api_client.post('/store/orders/', {
            'cart_id': str(cart_with_items.id)
        })

        order = Order.objects.first()
        assert order.items.count() == 1

        order_item = order.items.first()
        assert order_item.quantity == 2
        assert order_item.unit_price == Decimal('10.00')

    def test_cart_deleted_after_order(self, api_client, authenticated_user, cart_with_items):
        """Test that cart is deleted after successful order creation"""
        cart_id = cart_with_items.id

        api_client.post('/store/orders/', {
            'cart_id': str(cart_id)
        })

        assert not Cart.objects.filter(id=cart_id).exists()

    def test_cannot_create_order_from_empty_cart(self, api_client, authenticated_user):
        """Test that empty cart cannot create order"""
        empty_cart = baker.make(Cart)

        response = api_client.post('/store/orders/', {
            'cart_id': str(empty_cart.id)
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'empty' in response.data['cart_id'][0].lower()