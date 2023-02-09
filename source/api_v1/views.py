from rest_framework.viewsets import ModelViewSet

from webapp.models import Product
from api_v1.serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
