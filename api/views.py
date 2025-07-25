from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from decimal import Decimal

from .models import User, Dish, Order, OrderItem, Canteen, CanteenDish
from .permissions import IsCanteenWorker
from .serializers import (
    UserCreateSerializer, UserDetailSerializer, DishSerializer, 
    UserUpdateSerializer, OrderSerializer, CanteenSerializer, 
    CanteenMenuSerializer, OrderStatusUpdateSerializer, OrderCreateSerializer
)
from .authentication import JWTCookieAuthentication

# Функция для установки cookie
def set_jwt_cookies(response, user):
    refresh = RefreshToken.for_user(user)
    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
        secure=False, # В продакшене должно быть True
        samesite='Lax'
    )
    return response

# 1. create_user
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        response = Response(
            {"message": "Пользователь успешно создан"},
            status=status.HTTP_201_CREATED
        )
        set_jwt_cookies(response, user)
        return response

# 2. authorization
class AuthorizationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            response = Response(
                {"message": "Авторизация успешна"},
                status=status.HTTP_200_OK
            )
            set_jwt_cookies(response, user)
            return response
        
        return Response(
            {"error": "Неверные учетные данные"},
            status=status.HTTP_400_BAD_REQUEST
        )

# 3. get_user_info
class GetUserInfoView(views.APIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 3.1 update_user
class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Используем метод update из родительского класса, он обработает валидацию и сохранение
        response = super().update(request, *args, **kwargs)
        response.data = {"message": "Данные пользователя успешно обновлены."}
        return response

# 4. get_dish_info/id
#class GetDishInfoView(generics.RetrieveAPIView):
#    queryset = Dish.objects.filter(is_available=True)
#    serializer_class = DishSerializer
#    permission_classes = [AllowAny]
#    lookup_field = 'id' # Указываем, что в URL будет id

# 5. get_dishes_info
#class GetDishesInfoView(generics.ListAPIView):
#    queryset = Dish.objects.filter(is_available=True)
#    serializer_class = DishSerializer
#    permission_classes = [AllowAny]

class CanteenListView(generics.ListAPIView):
    queryset = Canteen.objects.all()
    serializer_class = CanteenSerializer
    permission_classes = [AllowAny]

class CanteenMenuView(generics.ListAPIView):
    serializer_class = CanteenMenuSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        canteen_id = self.kwargs.get('canteen_id')
        canteen_dishes = CanteenDish.objects.filter(
            canteen_id=canteen_id, 
            quantity__gt=0
        ).select_related('dish')

        dishes = []
        for cd in canteen_dishes:
            dish = cd.dish
            dish.available_quantity = cd.quantity 
            dishes.append(dish)
        
        return dishes

class CanteenMenuDetailView(generics.GenericAPIView):
    serializer_class = CanteenMenuSerializer
    permission_classes = [AllowAny]

    def get(self, request, canteen_id, dish_id):
        try:
            # Ищем конкретную запись об остатках для пары столовая-блюдо
            canteen_dish = CanteenDish.objects.select_related('dish').get(
                canteen_id=canteen_id,
                dish_id=dish_id
            )
        except CanteenDish.DoesNotExist:
            return Response({"error": "Блюдо не найдено в этой столовой"}, status=status.HTTP_404_NOT_FOUND)

        # "Прикрепляем" количество к объекту блюда для сериализатора
        dish = canteen_dish.dish
        dish.available_quantity = canteen_dish.quantity

        serializer = self.get_serializer(dish)
        return Response(serializer.data)

# 6. set_order
class SetOrderView(views.APIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        canteen_id = request.data.get('canteen_id')
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        items_data = validated_data.get('items', [])
        
        try:
            canteen = Canteen.objects.get(id=canteen_id, is_open=True)
        except Canteen.DoesNotExist:
            return Response(
                {"error": f"Столовая с ID {canteen_id} не найдена или закрыта"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not items_data:
            return Response({"error": "Список 'items' не может быть пустым"}, status=status.HTTP_400_BAD_REQUEST)

        dish_ids = [item.get('dish_id') for item in items_data]
        
        canteen_dishes = CanteenDish.objects.filter(
            canteen=canteen,
            dish_id__in=dish_ids
        ).select_for_update()

        canteen_dishes_map = {cd.dish_id: cd for cd in canteen_dishes}

        for item_data in items_data:
            dish_id = item_data.get('dish_id')
            quantity = item_data.get('quantity', 1)

            if not isinstance(dish_id, int) or not isinstance(quantity, int) or quantity <= 0:
                 return Response({"error": f"Некорректные данные для позиции: {item_data}"}, status=status.HTTP_400_BAD_REQUEST)

            if dish_id not in canteen_dishes_map:
                return Response({"error": f"Блюдо с ID {dish_id} не найдено в этой столовой"}, status=status.HTTP_404_NOT_FOUND)
            
            canteen_dish = canteen_dishes_map[dish_id]
            if canteen_dish.quantity < quantity:
                return Response({"error": f"Недостаточное количество блюда '{canteen_dish.dish.name}'. Доступно: {canteen_dish.quantity}"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user, 
            canteen=canteen, 
            status='new',
            preparation_type=validated_data.get('preparation_type', 'asap'),
            preparation_time=validated_data.get('preparation_time')
        )
        total_price = Decimal('0.0')

        order_items_to_create = []
        for item_data in items_data:
            dish_id = item_data['dish_id']
            quantity = item_data['quantity']
            canteen_dish = canteen_dishes_map[dish_id]

            canteen_dish.quantity -= quantity
            
            order_items_to_create.append(
                OrderItem(order=order, dish=canteen_dish.dish, quantity=quantity)
            )
            total_price += canteen_dish.dish.price * quantity

        CanteenDish.objects.bulk_update(canteen_dishes_map.values(), ['quantity'])
        OrderItem.objects.bulk_create(order_items_to_create)

        order.total_price = total_price
        order.status = 'paid'
        order.save()

        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

# API для выхода (удаление cookie)
class LogoutView(views.APIView):
    def post(self, request, *args, **kwargs):
        response = Response({"message": "Выход выполнен успешно"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        return response
    
class WorkerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsCanteenWorker]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(
            canteen=user.canteen, 
            status__in=['paid', 'new']
        ).prefetch_related('items__dish')

        # Сортируем: 'asap' заказы получают приоритет (0), 'scheduled' - (1)
        # Затем сортируем по времени создания для 'asap' и по времени готовки для 'scheduled'
        return sorted(
            queryset, 
            key=lambda order: (
                0 if order.preparation_type == 'asap' else 1,
                order.preparation_time if order.preparation_type == 'scheduled' and order.preparation_time else order.created_at
            )
        )

class WorkerOrderUpdateStatusView(generics.UpdateAPIView):
    serializer_class = OrderStatusUpdateSerializer
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsCanteenWorker]
    http_method_names = ['patch']

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(canteen=user.canteen)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)