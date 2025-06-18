from rest_framework import serializers

from DjangoProject.models import Newproduct, DiaryProduct


class NewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newproduct
        fields = '__all__'


class DairyProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiaryProduct
        fields = '__all__'