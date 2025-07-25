# Generated by Django 5.2.3 on 2025-07-22 19:54

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0015_alter_productimage_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentIntent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('razorpay_order_id', models.CharField(max_length=255, unique=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('status', models.CharField(choices=[('created', 'Created'), ('attempted', 'Attempted'), ('paid', 'Paid'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='created', max_length=20)),
                ('receipt', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('webhook_received', models.BooleanField(default=False)),
                ('webhook_data', models.JSONField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_intents', to='store.order')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=255, unique=True)),
                ('event_type', models.CharField(max_length=100)),
                ('data', models.JSONField()),
                ('processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_intent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.paymentintent')),
            ],
        ),
    ]
