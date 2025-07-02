from django.contrib import admin
from .models import User, Dish, Order, OrderItem, Canteen, CanteenDish


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['dish']
    extra = 1 # Количество пустых форм для добавления

class CanteenDishInline(admin.TabularInline):
    model = CanteenDish
    extra = 1

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'weight')
    search_fields = ('name',)
    inlines = [CanteenDishInline]

@admin.register(Canteen)
class CanteenAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_open')
    list_filter = ('is_open',)
    inlines = [CanteenDishInline]

admin.site.register(User)
admin.site.register(OrderItem)
admin.site.register(CanteenDish)