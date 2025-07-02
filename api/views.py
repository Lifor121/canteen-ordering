from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from decimal import Decimal

from .models import User, Dish, Order, OrderItem
from .serializers import (
    UserCreateSerializer, UserDetailSerializer, DishSerializer, 
    UserUpdateSerializer, OrderSerializer 
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
class GetDishInfoView(generics.RetrieveAPIView):
    queryset = Dish.objects.filter(is_available=True)
    serializer_class = DishSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id' # Указываем, что в URL будет id

# 5. get_dishes_info
class GetDishesInfoView(generics.ListAPIView):
    queryset = Dish.objects.filter(is_available=True)
    serializer_class = DishSerializer
    permission_classes = [AllowAny]

# 6. set_order
class SetOrderView(views.APIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Получаем список заказанных позиций
        items_data = request.data.get('items')
        
        # 2. Валидация входных данных
        if not isinstance(items_data, list) or not items_data:
            return Response(
                {"error": "Тело запроса должно содержать непустой список 'items'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Собираем все ID блюд из запроса для одного запроса к БД
        dish_ids = [item.get('dish_id') for item in items_data]

        # 3. Получаем все запрошенные блюда из БД одним запросом
        available_dishes = Dish.objects.filter(id__in=dish_ids, is_available=True)
        
        # Создаем словарь для быстрого доступа к объектам блюд по их ID
        dishes_map = {dish.id: dish for dish in available_dishes}

        # 4. Проверяем, все ли блюда существуют и доступны
        requested_ids_set = set(dish_ids)
        found_ids_set = set(dishes_map.keys())

        if requested_ids_set != found_ids_set:
            missing_ids = requested_ids_set - found_ids_set
            return Response(
                {"error": f"Блюда с ID {list(missing_ids)} не найдены или недоступны"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 5. Создаем заказ и его позиции
        order = Order.objects.create(user=request.user, status='new')
        total_price = Decimal('0.0')

        order_items_to_create = []
        for item_data in items_data:
            dish_id = item_data.get('dish_id')
            quantity = item_data.get('quantity', 1) # По умолчанию 1, если не указано
            
            # Проверяем корректность данных
            if not isinstance(dish_id, int) or not isinstance(quantity, int) or quantity <= 0:
                order.delete()
                return Response(
                    {"error": f"Некорректные данные для позиции: {item_data}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Получаем объект блюда из нашего словаря
            dish = dishes_map[dish_id]
            
            # Добавляем позицию заказа в список для массового создания
            order_items_to_create.append(
                OrderItem(order=order, dish=dish, quantity=quantity)
            )
            # Считаем итоговую стоимость
            total_price += dish.price * quantity
        
        # 6. Массово создаем все позиции заказа одним запросом к БД
        OrderItem.objects.bulk_create(order_items_to_create)

        # Обновляем итоговую стоимость и статус заказа
        order.total_price = total_price
        order.status = 'paid'  # Симуляция успешной оплаты
        order.save()
        
        # Сериализуем созданный заказ для ответа
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# API для выхода (удаление cookie)
class LogoutView(views.APIView):
    def post(self, request, *args, **kwargs):
        response = Response({"message": "Выход выполнен успешно"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        return response