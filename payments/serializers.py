from rest_framework import serializers
from .models import PaymentIntent
from .services import RazorpayService
from store.models import Order
from decimal import Decimal


class CreatePaymentIntentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            if order.payment_status == Order.PAYMENT_STATUS_COMPLETE:
                raise serializers.ValidationError("Order is already paid")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")

    def create(self, validated_data):
        order = Order.objects.get(id=validated_data['order_id'])

        # Calculate total amount
        total_amount = sum(item.quantity * item.unit_price for item in order.items.all())
        amount_in_paise = int(total_amount * 100)  # Convert to paise

        # Create Razorpay order
        razorpay_service = RazorpayService()
        razorpay_order = razorpay_service.create_order(order, amount_in_paise)

        # Create PaymentIntent
        payment_intent = PaymentIntent.objects.create(
            order=order,
            razorpay_order_id=razorpay_order['id'],
            amount=total_amount,
            receipt=razorpay_order['receipt']
        )

        return payment_intent


class PaymentIntentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentIntent
        fields = [
            'id', 'order_id', 'razorpay_order_id', 'amount', 'currency',
            'status', 'receipt', 'customer_name', 'created_at'
        ]

    def get_customer_name(self, obj):
        return f"{obj.order.customer.user.first_name} {obj.order.customer.user.last_name}"


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()

    def validate(self, data):
        # Check if payment intent exists
        try:
            payment_intent = PaymentIntent.objects.get(
                razorpay_order_id=data['razorpay_order_id']
            )
        except PaymentIntent.DoesNotExist:
            raise serializers.ValidationError("Payment intent not found")

        # Verify signature
        razorpay_service = RazorpayService()
        is_valid = razorpay_service.verify_payment(
            data['razorpay_order_id'],
            data['razorpay_payment_id'],
            data['razorpay_signature']
        )

        if not is_valid:
            raise serializers.ValidationError("Invalid payment signature")

        data['payment_intent'] = payment_intent
        return data