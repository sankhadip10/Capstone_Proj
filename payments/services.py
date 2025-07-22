import razorpay
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, order, amount_in_paise):
        """Create a Razorpay order"""
        try:
            data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'order_{order.id}',
                'notes': {
                    'order_id': str(order.id),
                    'customer_email': order.customer.user.email,
                    'customer_name': f"{order.customer.user.first_name} {order.customer.user.last_name}"
                }
            }

            razorpay_order = self.client.order.create(data)
            logger.info(f"Razorpay order created: {razorpay_order['id']}")
            return razorpay_order

        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}")
            raise

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature"""
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            self.client.utility.verify_payment_signature(params_dict)
            return True

        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return False

    def fetch_payment(self, payment_id):
        """Fetch payment details from Razorpay"""
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            logger.error(f"Failed to fetch payment {payment_id}: {e}")
            return None

    def refund_payment(self, payment_id, amount=None):
        """Create a refund"""
        try:
            data = {}
            if amount:
                data['amount'] = amount

            refund = self.client.payment.refund(payment_id, data)
            logger.info(f"Refund created: {refund['id']}")
            return refund

        except Exception as e:
            logger.error(f"Failed to create refund: {e}")
            raise