from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from decimal import Decimal

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Студент'),
        ('worker', 'Сотрудник столовой'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

class Dish(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название блюда")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    weight = models.PositiveIntegerField(verbose_name="Вес (в граммах)")
    photo = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name="Фото")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('ready', 'Готов к выдаче'),
        ('closed', 'Закрыт'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Итоговая цена")

    def __str__(self):
        return f"Заказ №{self.id} от {self.user.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='order_items', verbose_name="Блюдо")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} в заказе №{self.order.id}"
    
    def get_cost(self):
        return self.dish.price * self.quantity

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"