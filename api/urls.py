from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet, OrderViewSet, AdminOrderViewSet

router = DefaultRouter()
router.register(r'dishes', DishViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'admin/orders', AdminOrderViewSet, basename='admin-order')


urlpatterns = [
    path('', include(router.urls)),
]