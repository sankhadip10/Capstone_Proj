from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from DjangoProject.models import Newproduct, DiaryProduct
from DjangoProject.new_product_serializer import NewProductSerializer, DairyProductSerializer


class ListCreateProductAPIView(APIView):

    def get(self,request):
        # products = Newproduct.objects.all().filter(price__gt=30)
        # .filter(price__range=[60.0,100.0])
        products = Newproduct.objects.raw('SELECT * FROM djangoproject_Newproduct WHERE price BETWEEN 80.0 AND 100.0')

        serialized = NewProductSerializer(products, many=True)
        return Response(serialized.data,status=200)


    def post(self,request):
        data = request.data
        decoded_data = NewProductSerializer(data=data)
        if not decoded_data.is_valid():
            return Response(decoded_data.errors, status=400)

        decoded_data.save()
        return Response(decoded_data.data, status=201)

class DairyListCreateAPIView(ListCreateAPIView):
    queryset = DiaryProduct.objects.all()
    serializer_class = DairyProductSerializer


class DairyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = DiaryProduct.objects.all()
    serializer_class = DairyProductSerializer