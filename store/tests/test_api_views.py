import pytest
from decimal import Decimal
from rest_framework import status
from model_bakery import baker


@pytest.mark.django_db
class TestAPIViews:

    def test_product_list_view(self, api_client, product):
        """Test product list endpoint"""
        response = api_client.get('/store/products/')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1

    def test_product_detail_view(self, api_client, product):
        """Test product detail endpoint"""
        response = api_client.get(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
        assert response.data['title'] == product.title

    def test_collection_list_view(self, api_client, collection):
        """Test collection list endpoint"""
        response = api_client.get('/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_cart_creation(self, api_client):
        """Test cart creation endpoint"""
        response = api_client.post('/store/carts/', {})

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['total_price'] == '0.00'

    def test_add_item_to_cart(self, api_client, product):
        """Test adding item to cart"""
        # Create cart first
        cart_response = api_client.post('/store/carts/', {})
        cart_id = cart_response.data['id']

        # Add item to cart
        response = api_client.post(f'/store/carts/{cart_id}/items/', {
            'product_id': product.id,
            'quantity': 2
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 2

    def test_cart_total_calculation(self, api_client, product):
        """Test cart total price calculation"""
        # Create cart and add item
        cart_response = api_client.post('/store/carts/', {})
        cart_id = cart_response.data['id']

        api_client.post(f'/store/carts/{cart_id}/items/', {
            'product_id': product.id,
            'quantity': 2
        })

        # Check cart total
        response = api_client.get(f'/store/carts/{cart_id}/')

        assert response.status_code == status.HTTP_200_OK
        expected_total = str(product.unit_price * 2)
        assert response.data['total_price'] == expected_total

    def test_order_creation_requires_auth(self, api_client, cart_with_items):
        """Test that order creation requires authentication"""
        response = api_client.post('/store/orders/', {
            'cart_id': str(cart_with_items.id)
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_order_creation(self, api_client, authenticated_user, cart_with_items):
        """Test order creation with authentication"""
        response = api_client.post('/store/orders/', {
            'cart_id': str(cart_with_items.id)
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['customer'] is not None