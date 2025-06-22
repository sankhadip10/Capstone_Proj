from django.db import models

class UserFlipkart(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    # shipping_address = models.TextField()
    # billing_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    default_shipping_address = models.ForeignKey(
        "ShippingAddress",
        on_delete=models.DO_NOTHING,
        null=True,
        related_query_name="user_info"
    )


    def __str__(self):
        return self.name

class AddressFlipkart(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        abstract = True


class ShippingAddress(AddressFlipkart):
    user_flipkart = models.ForeignKey(
        UserFlipkart,
        on_delete=models.CASCADE,
        related_name='shipping_addresses'
    )

