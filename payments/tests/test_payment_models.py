import pytest
from decimal import Decimal
from model_bakery import baker

# Only run if payments app exists
try:
    from payments.models import PaymentIntent


    @pytest.mark.django_db
    class TestPaymentModels:

        def test_payment_intent_creation(self, order):
            """Test PaymentIntent creation"""
            payment_intent = baker.make(PaymentIntent,
                                        order=order,
                                        razorpay_order_id='order_test123',
                                        amount=Decimal('10.00'))

            assert payment_intent.order == order
            assert payment_intent.razorpay_order_id == 'order_test123'
            assert payment_intent.amount == Decimal('10.00')
            assert payment_intent.status == 'created'  # default

except ImportError:
    # Payments app not yet created
    pass