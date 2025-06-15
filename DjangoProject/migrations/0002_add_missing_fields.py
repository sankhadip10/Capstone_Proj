from django.db import migrations, models


def populate_empty_addresses(apps, schema_editor):
    """Fill empty address fields with default value"""
    User = apps.get_model('DjangoProject', 'User')
    User.objects.filter(address__isnull=True).update(address='')
    User.objects.filter(address='').update(address='Not provided')


class Migration(migrations.Migration):
    dependencies = [
        ('DjangoProject', '0001_initial'),
    ]

    operations = [
        # First, populate any empty addresses
        migrations.RunPython(populate_empty_addresses, reverse_code=migrations.RunPython.noop),

        # Add the missing title field
        migrations.AddField(
            model_name='user',
            name='title',
            field=models.CharField(
                choices=[('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms')],
                default='Mr',
                max_length=50
            ),
        ),
        # Update field lengths to match current model
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.CharField(max_length=255),
        ),
    ]