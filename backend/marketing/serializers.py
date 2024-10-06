from .models import ProductsDetail
from rest_framework import serializers


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsDetail
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
class ProductsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsDetail
        fields = ['id', 'productname', 'productlogo']

        