from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from DjangoProject.json_models import NewProductJson
from DjangoProject.json_serializer import ProductSerializer
# def say_hello_to(request):
#     print("This is within view")
#     return HttpResponse("Hello world")

class ProductListCreateAPIView(ListCreateAPIView):
    queryset = NewProductJson.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = ([IsAuthenticated])

class EmptyException(Exception):
    pass


class ProductList(APIView):
    def get(self):
        products = NewProductJson.objects.all()
        if len(products) == 0:
            raise EmptyException()

        return ProductSerializer(products, many=True)


