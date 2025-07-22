from django.urls import path
from . import views

urlpatterns = [
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('verify-payment/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('webhook/', views.RazorpayWebhookView.as_view(), name='razorpay-webhook'),
    path('status/<int:order_id>/', views.PaymentStatusView.as_view(), name='payment-status'),
]