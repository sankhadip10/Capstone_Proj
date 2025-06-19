from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from DjangoProject.models import UserFlipkart,ShippingAddress
from DjangoProject.new_product_serializer import FlipkartUserSerializer,ShippingAddressSerializer
from DjangoProject.new_product_serializer import CreateShippingAddressSerializer,UserSerializer

from django.shortcuts import get_object_or_404
class UserListCreateAPIView(ListCreateAPIView):
    queryset = UserFlipkart.objects.all()
    serializer_class = FlipkartUserSerializer

class UserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = UserFlipkart.objects.all()
    serializer_class = UserSerializer

class ShippingAddressListCreateAPIView(APIView):
    serializer_class = CreateShippingAddressSerializer
    def post(self, request,user_id):
        user = get_object_or_404(UserFlipkart, pk=user_id)
        serialized = CreateShippingAddressSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(serialized.errors, status=400)

        shipping_address = ShippingAddress(
            street=serialized.data['street'],
            city=serialized.data['city'],
            state=serialized.data['state'],
            zipcode=serialized.data['zipcode'],
            country=serialized.data['country'],
            user_flipkart=user
        )

        shipping_address.save()

        return Response(ShippingAddressSerializer(shipping_address).data, status=201)
