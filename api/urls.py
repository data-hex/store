from django.urls import path, include
from api.views import ProductModelViewSet, BasketModelViewSet

from rest_framework import routers

app_name = 'api'
router = routers.DefaultRouter()
router.register(r'products', ProductModelViewSet)
router.register(r'baskets', BasketModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]