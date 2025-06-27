from django.contrib import admin
from .models import User, Dish, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['dish']
    extra = 1 # Количество пустых форм для добавления

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'weight', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)

admin.site.register(User)
admin.site.register(OrderItem)