# Generated by Django 5.2.3 on 2025-06-30 22:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_customer_options_remove_customer_email_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': [('cancel_order', 'Can cancel order')]},
        ),
    ]
