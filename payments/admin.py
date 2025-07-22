from django.contrib import admin
from .models import PaymentIntent, WebhookEvent

@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ['razorpay_order_id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['razorpay_order_id', 'razorpay_payment_id', 'order__id']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'event_id', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    readonly_fields = ['created_at']