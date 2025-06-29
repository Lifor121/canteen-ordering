from rest_framework import serializers
from .models import Dish, Order, OrderItem, User


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
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Проверяем, что оба пароля совпадают
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        # Создаем пользователя с помощью метода create_user, который хэширует пароль
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            # Устанавливаем роль по умолчанию
            role='student' 
        )
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    # Вкладываем сериализатор заказов, чтобы получить список заказов пользователя
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'role', 'orders')