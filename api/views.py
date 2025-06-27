from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Dish, Order
from .serializers import DishSerializer, OrderSerializer, OrderCreateSerializer

# Только для просмотра меню (доступно всем)
class DishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dish.objects.filter(is_available=True)
    serializer_class = DishSerializer

# Для управления заказами пользователей
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пользователь видит только свои заказы
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # Для создания используем один сериализатор, для просмотра - другой
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        # Передаем user в контексте сериализатора
        serializer.save(user=self.request.user)


# Для управления ВСЕМИ заказами
class AdminOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]