from rest_framework import serializers
from webapp.models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'amount', 'price']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'name', 'phone', 'address', 'created_at', 'products', 'client']
        read_only_fields = ['id', 'created_at']
