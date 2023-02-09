from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

DEFAULT_CATEGORY = 'other'
CATEGORY_CHOICES = ((DEFAULT_CATEGORY, 'разное'), ('food', 'еда'), ('drinks', 'напитки'), ('sweets', 'сладости'),)


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название товара')
    description = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Описание товара')
    category = models.CharField(max_length=30, default=DEFAULT_CATEGORY, choices=CATEGORY_CHOICES,
                                verbose_name='Категория товара')
    amount = models.PositiveIntegerField(verbose_name='Остаток товара')
    price = models.DecimalField(verbose_name='Цена товара', max_digits=7, decimal_places=2,
                                validators=(MinValueValidator(0),))

    def __str__(self):
        return f'{self.name} - {self.amount}'


class Cart(models.Model):
    product = models.ForeignKey('webapp.Product', on_delete=models.CASCADE,
                                verbose_name='Товар', related_name='in_cart')
    qty = models.PositiveIntegerField(verbose_name='Количество', default=1)
    user_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='carts', blank=True, null=True)

    def __str__(self):
        return f'{self.product.name} - {self.qty}'

    def get_product_total(self):
        return self.qty * self.product.price

    @classmethod
    def get_total(cls):
        total = 0
        for cart in cls.objects.all():
            total += cart.get_product_total()
        return total


class Order(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    phone = models.CharField(max_length=30, verbose_name='Телефон')
    address = models.CharField(max_length=100, verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    products = models.ManyToManyField('webapp.Product', related_name='orders', verbose_name='Товары',
                                      through='webapp.OrderProduct', through_fields=['order', 'product'])
    client = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, verbose_name="Клиент")

    def __str__(self):
        return f'{self.name} - {self.phone}'


class OrderProduct(models.Model):
    product = models.ForeignKey('webapp.Product', on_delete=models.CASCADE,
                                verbose_name='Товар', related_name='order_prods')
    order = models.ForeignKey('webapp.Order', on_delete=models.CASCADE,
                              verbose_name='Заказ', related_name='order_products')
    qty = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.product.name}'
