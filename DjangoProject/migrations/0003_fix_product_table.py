from django.db import migrations, models
import django.db.models.deletion


def set_default_seller(apps, schema_editor):
    """Set a default seller for existing products"""
    Product = apps.get_model('DjangoProject', 'Product')
    User = apps.get_model('DjangoProject', 'User')

    # Get the first user to use as default seller
    try:
        default_user = User.objects.first()
        if default_user:
            # Update all existing products to have this user as seller
            Product.objects.filter(seller__isnull=True).update(seller=default_user)
    except:
        pass  # If no users exist, we'll handle it later


class Migration(migrations.Migration):
    dependencies = [
        ('DjangoProject', '0002_add_missing_fields'),
    ]

    operations = [
        # Add the missing seller foreign key field
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(
                default=1,  # Default to user with ID 1
                on_delete=django.db.models.deletion.CASCADE,
                to='DjangoProject.user'
            ),
            preserve_default=False,
        ),

        # Add the missing stock field
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.IntegerField(default=0),
        ),

        # Update field lengths to match current model
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(max_length=255),
        ),

        # Set default seller for existing products
        migrations.RunPython(set_default_seller, reverse_code=migrations.RunPython.noop),
    ]