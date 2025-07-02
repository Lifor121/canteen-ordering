from rest_framework import serializers
from .models import Dish, Order, OrderItem, User, Canteen, CanteenDish
import re

class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = ('id', 'name', 'address', 'is_open')

class CanteenMenuSerializer(serializers.ModelSerializer):
    # Добавляем поле, которого нет в модели, но которое мы вычислим во view
    available_quantity = serializers.IntegerField()

    class Meta:
        model = Dish
        fields = ('id', 'name', 'description', 'price', 'weight', 'photo', 'available_quantity')

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ('id', 'name', 'description', 'price', 'weight', 'photo', 'is_available')

class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source='dish.name')
    dish_price = serializers.DecimalField(source='dish.price', max_digits=8, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = ('dish_name', 'dish_price', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'status', 'created_at', 'total_price', 'items')

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Метод create_user автоматически хэширует пароль
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            # Устанавливаем роль по умолчанию
            role='student'
        )
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'role', 'canteen', 'orders')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

    def validate(self, data):
        for field, value in data.items():
            if value and re.search(r'\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b', value, re.IGNORECASE):
                raise serializers.ValidationError(
                    f"Поле '{field}' должно содержать корректные данные."
                )
        return data
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        # Работник может менять статус только на 'ready' или 'closed'
        if value not in ['ready', 'closed']:
            raise serializers.ValidationError("Недопустимый статус. Доступные статусы: 'ready', 'closed'.")
        return value