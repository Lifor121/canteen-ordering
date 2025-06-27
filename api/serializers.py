from rest_framework import serializers
from .models import Dish, Order, OrderItem, User

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ('id', 'name', 'description', 'price', 'weight', 'photo', 'is_available')

class OrderItemSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True) # Показываем полную информацию о блюде
    
    class Meta:
        model = OrderItem
        fields = ('id', 'dish', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) # Вложенные позиции заказа
    user = serializers.StringRelatedField() # Показываем имя пользователя

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'created_at', 'total_price', 'items')

# Сериализатор для создания заказа
class OrderCreateSerializer(serializers.ModelSerializer):
    # Клиент будет присылать список ID блюд и их количество
    items = serializers.JSONField() 
    
    class Meta:
        model = Order
        fields = ('items',)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Создаем заказ
        order = Order.objects.create(user=user, status='new')
        total_price = 0

        # Создаем позиции заказа
        for item_data in items_data:
            dish = Dish.objects.get(id=item_data['dish_id'])
            quantity = item_data['quantity']
            order_item = OrderItem.objects.create(order=order, dish=dish, quantity=quantity)
            total_price += order_item.get_cost()
            
        order.total_price = total_price
        order.status = 'paid' # Предполагаем, что оплата прошла
        order.save()
        return order