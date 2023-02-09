from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser, AllowAny

from webapp.models import Product, Order
from api_v1.serializers import ProductSerializer, OrderSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        elif self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return super().get_permissions()


class CustomPermission(BasePermission):
    message = "You do not have permission for this action!"

    def has_permission(self, request, view):
        if request.method == "POST" and not request.user.is_staff:
            return True
        elif request.method == "GET" and request.user.is_staff:
            return True
        return False


class OrderView(APIView):
    permission_classes = [CustomPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            order = get_object_or_404(Order, pk=kwargs.get('pk'))
            serializer = OrderSerializer(order)
        else:
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
