from django.urls import path, include
from api_v1.views import ProductViewSet, OrderView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api_v1'

router = DefaultRouter()
router.register('products', ProductViewSet)

order_url = [
    path('', OrderView.as_view()),
    path('<int:pk>/', OrderView.as_view()),
]

urlpatterns = [
    path('', include(router.urls)),
    path('order/', include(order_url)),
    path('login/', obtain_auth_token, name='api_token_auth'),
]
