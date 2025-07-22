import pytest
from decimal import Decimal
from model_bakery import baker
from django.db.models import Count

from store.serializers import (
    ProductSerializer, CollectionSerializer, CartSerializer,
    CartItemSerializer, AddCartItemSerializer, OrderSerializer,
    CreateOrderSerializer
)
from store.models import Collection, Product, Cart, CartItem


@pytest.mark.django_db
class TestSerializers:

    def test_product_serializer(self):
        """Test ProductSerializer"""
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)

        serializer = ProductSerializer(instance=product)
        data = serializer.data

        assert data['id'] == product.id
        assert data['title'] == product.title
        assert Decimal(data['unit_price']) == product.unit_price
        assert 'price_wih_tax' in data

    def test_collection_serializer(self):
        """Test CollectionSerializer with products_count"""
        collection = baker.make(Collection)

        # FIXED: Add annotation for products_count like in your view
        from django.db.models import Count
        collection_with_count = Collection.objects.annotate(
            products_count=Count('products')
        ).get(id=collection.id)

        serializer = CollectionSerializer(instance=collection_with_count)
        data = serializer.data

        assert data['id'] == collection.id
        assert data['title'] == collection.title
        assert 'products_count' in data
        assert data['products_count'] == 0

    def test_cart_serializer(self):
        """Test CartSerializer"""
        cart = baker.make(Cart)
        serializer = CartSerializer(instance=cart)
        data = serializer.data

        assert str(data['id']) == str(cart.id)
        assert data['items'] == []
        # FIXED: Handle string vs decimal comparison
        total_price = data['total_price']
        if isinstance(total_price, str):
            assert total_price == '0.00'
        else:
            assert total_price == 0

    def test_add_cart_item_serializer_valid_data(self):
        """Test AddCartItemSerializer with valid data"""
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)

        data = {'product_id': product.id, 'quantity': 2}
        serializer = AddCartItemSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data['product_id'] == product.id
        assert serializer.validated_data['quantity'] == 2

    def test_add_cart_item_serializer_invalid_product(self):
        """Test AddCartItemSerializer with invalid product"""
        data = {'product_id': 99999, 'quantity': 2}
        serializer = AddCartItemSerializer(data=data)

        assert not serializer.is_valid()
        assert 'product_id' in serializer.errors

    def test_create_order_serializer_valid_cart(self):
        """Test CreateOrderSerializer with valid cart"""
        cart = baker.make(Cart)
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)
        baker.make(CartItem, cart=cart, product=product, quantity=1)

        data = {'cart_id': cart.id}
        serializer = CreateOrderSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data['cart_id'] == cart.id

    def test_create_order_serializer_empty_cart(self):
        """Test CreateOrderSerializer with empty cart"""
        cart = baker.make(Cart)
        data = {'cart_id': cart.id}
        serializer = CreateOrderSerializer(data=data)

        assert not serializer.is_valid()
        assert 'cart_id' in serializer.errors