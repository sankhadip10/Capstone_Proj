import pytest
from decimal import Decimal
from model_bakery import baker
from django.contrib.auth import get_user_model

from store.models import Product, Collection, Customer, Order, OrderItem, Cart, CartItem

User = get_user_model()


@pytest.mark.django_db
class TestModels:

    def test_user_model_creation(self):
        """Test User model creation"""
        user = baker.make(User, email='test@example.com')
        assert user.email == 'test@example.com'
        assert user.id is not None

    def test_customer_model_creation(self):
        """Test Customer model creation"""
        # Create user and customer separately (no signal)
        user = baker.make(User, email='customer@example.com')
        customer = baker.make(Customer, user=user)
        assert customer.user == user
        assert customer.membership == Customer.MEMBERSHIP_BRONZE

    def test_customer_str_method(self):
        """Test Customer string representation"""
        user = baker.make(User, first_name='John', last_name='Doe')
        customer = baker.make(Customer, user=user)
        expected = f"{user.first_name} {user.last_name}"
        assert str(customer) == expected

    def test_collection_model_creation(self):
        """Test Collection model creation"""
        collection = baker.make(Collection, title='Electronics')
        assert collection.title == 'Electronics'
        assert str(collection) == 'Electronics'

    def test_product_model_creation(self):
        """Test Product model creation"""
        collection = baker.make(Collection)
        product = baker.make(Product,
                             title='Laptop',
                             unit_price=Decimal('999.99'),
                             inventory=10,
                             collection=collection)

        assert product.title == 'Laptop'
        assert product.unit_price == Decimal('999.99')
        assert product.inventory == 10
        assert product.collection == collection
        assert str(product) == 'Laptop'

    def test_order_model_creation(self):
        """Test Order model creation"""
        user = baker.make(User)
        customer = baker.make(Customer, user=user)  # Explicit creation
        order = baker.make(Order, customer=customer)
        assert order.customer == customer
        assert order.payment_status == Order.PAYMENT_STATUS_PENDING

    def test_order_item_creation(self):
        """Test OrderItem creation"""
        user = baker.make(User)
        customer = baker.make(Customer, user=user)  # Explicit creation
        order = baker.make(Order, customer=customer)
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)

        order_item = baker.make(OrderItem,
                                order=order,
                                product=product,
                                quantity=2,
                                unit_price=product.unit_price)

        assert order_item.order == order
        assert order_item.product == product
        assert order_item.quantity == 2
        assert order_item.unit_price == product.unit_price

    def test_cart_creation(self):
        """Test Cart creation"""
        cart = baker.make(Cart)
        assert cart.id is not None
        assert cart.created_at is not None

    def test_cart_item_creation(self):
        """Test CartItem creation"""
        cart = baker.make(Cart)
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)

        cart_item = baker.make(CartItem,
                               cart=cart,
                               product=product,
                               quantity=3)

        assert cart_item.cart == cart
        assert cart_item.product == product
        assert cart_item.quantity == 3
