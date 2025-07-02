from django.urls import path
from .views import (
    CreateUserView,
    AuthorizationView,
    GetUserInfoView,
    UpdateUserView,
    GetDishInfoView,
    GetDishesInfoView,
    SetOrderView,
    LogoutView,
)

urlpatterns = [
    path('create_user', CreateUserView.as_view(), name='create_user'),
    path('authorization', AuthorizationView.as_view(), name='authorization'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('get_user_info', GetUserInfoView.as_view(), name='get_user_info'),
    path('update_user', UpdateUserView.as_view(), name='update_user'),
    path('get_dish_info/<int:id>', GetDishInfoView.as_view(), name='get_dish_info'),
    path('get_dishes_info', GetDishesInfoView.as_view(), name='get_dishes_info'),
    path('set_order', SetOrderView.as_view(), name='set_order'),
]