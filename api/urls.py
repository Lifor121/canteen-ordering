from django.urls import path
from .views import (
    CreateUserView,
    AuthorizationView,
    GetUserInfoView,
    UpdateUserView,
    CanteenListView,
    CanteenMenuView,
    CanteenMenuDetailView,
    #GetDishInfoView,
    #GetDishesInfoView,
    SetOrderView,
    LogoutView,
    WorkerOrderListView,
    WorkerOrderUpdateStatusView
)

urlpatterns = [
    path('create_user', CreateUserView.as_view(), name='create_user'),
    path('authorization', AuthorizationView.as_view(), name='authorization'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('get_user_info', GetUserInfoView.as_view(), name='get_user_info'),
    path('update_user', UpdateUserView.as_view(), name='update_user'),
    #path('get_dish_info/<int:id>', GetDishInfoView.as_view(), name='get_dish_info'),
    #path('get_dishes_info', GetDishesInfoView.as_view(), name='get_dishes_info'),
    path('canteens', CanteenListView.as_view(), name='canteen-list'),
    path('canteens/<int:canteen_id>/menu', CanteenMenuView.as_view(), name='canteen-menu'),
    path('canteens/<int:canteen_id>/menu/<int:dish_id>', CanteenMenuDetailView.as_view(), name='canteen-menu-detail'),
    path('set_order', SetOrderView.as_view(), name='set_order'),
    path('worker/orders', WorkerOrderListView.as_view(), name='worker-order-list'),
    path('worker/orders/<int:pk>/update-status', WorkerOrderUpdateStatusView.as_view(), name='worker-order-update'),
]