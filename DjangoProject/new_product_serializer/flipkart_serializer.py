from rest_framework import serializers
from DjangoProject.models import UserFlipkart,ShippingAddress

class FlipkartUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFlipkart
        fields = '__all__'

class CreateShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["street", "city", "state", "zipcode", "country"]

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    shipping_addresses = ShippingAddressSerializer(many=True)
    default_shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = UserFlipkart
        fields = '__all__'