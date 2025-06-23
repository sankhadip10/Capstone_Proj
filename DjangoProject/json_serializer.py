from DjangoProject.json_models import NewProductJson

from rest_framework.serializers import ModelSerializer

class ProductSerializer(ModelSerializer):
    class Meta:
        model = NewProductJson
        fields = '__all__'