import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker
from decimal import Decimal
from django.db.models.signals import post_save
from django.test.utils import override_settings

from store.models import Customer, Product, Collection, Cart, CartItem, Order, OrderItem

User = get_user_model()


# WORKING SOLUTION: Disconnect the specific signal at the start of tests
@pytest.fixture(autouse=True, scope='session')
def disconnect_signals():
    """Disconnect the customer creation signal for all tests"""
    # Import the actual signal handler
    from core.signals.handlers import create_customer_for_new_user

    # Disconnect it completely
    post_save.disconnect(create_customer_for_new_user, sender=User)

    yield

    # Optionally reconnect after tests (though not necessary for tests)
    # post_save.connect(create_customer_for_new_user, sender=User)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    """Create a basic user - no customer will be auto-created"""
    return baker.make(User,
                      username='testuser',
                      email='test@example.com',
                      first_name='Test',
                      last_name='User')


@pytest.fixture
def customer(user):
    """Create customer explicitly - no signal interference"""
    return baker.make(Customer,
                      user=user,
                      membership=Customer.MEMBERSHIP_BRONZE,
                      phone='+1234567890')


@pytest.fixture
def authenticated_user(api_client, user, customer):
    """Authenticated user with customer for API tests"""
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def collection():
    """Create a test collection"""
    return baker.make(Collection, title='Test Collection')


@pytest.fixture
def product(collection):
    """Create a test product"""
    return baker.make(Product,
                      title='Test Product',
                      slug='test-product',
                      unit_price=Decimal('10.00'),
                      inventory=50,
                      collection=collection)


@pytest.fixture
def cart():
    """Create an empty cart"""
    return baker.make(Cart)


@pytest.fixture
def cart_with_items(cart, product):
    """Create cart with items"""
    cart_item = baker.make(CartItem,
                           cart=cart,
                           product=product,
                           quantity=2)
    return cart


@pytest.fixture
def order(customer):
    """Create a test order"""
    return baker.make(Order,
                      customer=customer,
                      payment_status=Order.PAYMENT_STATUS_PENDING)


@pytest.fixture
def order_with_items(order, product):
    """Create order with items"""
    order_item = baker.make(OrderItem,
                            order=order,
                            product=product,
                            quantity=2,
                            unit_price=product.unit_price)
    return order


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)

    return do_create_collection