import pytest
from unittest.mock import patch, Mock
from decimal import Decimal

from model_bakery import baker

from core.models import User
from payments.models import PaymentIntent, WebhookEvent
from payments.serializers import CreatePaymentIntentSerializer, VerifyPaymentSerializer
from payments.services import RazorpayService
from store.models import Order, Customer, Product, OrderItem


@pytest.mark.django_db
class TestPaymentIntegration:

    @pytest.fixture
    def order_for_payment(self):
        """Create order ready for payment"""
        user = baker.make(User)
        customer = baker.make(Customer, user=user)
        order = baker.make(Order, customer=customer, payment_status=Order.PAYMENT_STATUS_PENDING)

        product = baker.make(Product, unit_price=Decimal('20.00'))
        baker.make(OrderItem, order=order, product=product, quantity=1, unit_price=product.unit_price)

        return order

    @patch('payments.services.razorpay.Client')
    def test_create_payment_intent(self, mock_razorpay_client, order_for_payment):
        """Test creating payment intent"""
        # Mock Razorpay response
        mock_client = Mock()
        mock_client.order.create.return_value = {
            'id': 'order_test123',
            'receipt': f'order_{order_for_payment.id}'
        }
        mock_razorpay_client.return_value = mock_client

        serializer = CreatePaymentIntentSerializer(data={'order_id': order_for_payment.id})
        assert serializer.is_valid()

        payment_intent = serializer.save()

        assert payment_intent.order == order_for_payment
        assert payment_intent.razorpay_order_id == 'order_test123'
        assert payment_intent.amount == Decimal('20.00')

    @patch('payments.services.razorpay.Client')
    def test_verify_payment_success(self, mock_razorpay_client, order_for_payment):
        """Test successful payment verification"""
        # Create payment intent
        payment_intent = baker.make(PaymentIntent,
                                    order=order_for_payment,
                                    razorpay_order_id='order_test123',
                                    status='created')

        # Mock successful verification
        mock_client = Mock()
        mock_client.utility.verify_payment_signature.return_value = None  # No exception = success
        mock_razorpay_client.return_value = mock_client

        serializer = VerifyPaymentSerializer(data={
            'razorpay_order_id': 'order_test123',
            'razorpay_payment_id': 'pay_test123',
            'razorpay_signature': 'valid_signature'
        })

        assert serializer.is_valid()

        # Check that payment intent is found
        assert serializer.validated_data['payment_intent'] == payment_intent

    def test_webhook_event_creation(self):
        """Test webhook event storage"""
        webhook_data = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_webhook123',
                        'order_id': 'order_webhook123'
                    }
                }
            }
        }

        webhook_event = WebhookEvent.objects.create(
            event_id='pay_webhook123',
            event_type='payment.captured',
            data=webhook_data
        )

        assert webhook_event.event_type == 'payment.captured'
        assert webhook_event.data['event'] == 'payment.captured'
        assert not webhook_event.processed