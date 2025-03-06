from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from orders.models import DeliveryMethod


class User(AbstractUser ):
    phone = models.CharField(
        max_length=15,  # Увеличьте длину, чтобы учесть символы + и пробелы
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r'^(?:\+7|8)\d{10}$',  # Регулярное выражение для +7 или 8 и 10 цифр
                message='Телефон должен начинаться с +7 или 8 и содержать 10 цифр.'
            )
        ]
    )
    
    region = models.CharField(max_length=250, verbose_name="Регион")
    city = models.CharField(max_length=100, verbose_name="Город")
    address = models.CharField(max_length=250, verbose_name="Адрес")
    postal_code = models.CharField(
        max_length=6,
        verbose_name="Почтовый индекс",
        validators=[
            RegexValidator(
                regex=r'^\d+$',  # Исправлено
                message='Индекс должен состоять только из цифр.'
            )
        ]
    )

    delivery_method = models.ForeignKey(DeliveryMethod, blank=False, on_delete=models.SET_NULL, null=True, verbose_name="Способ доставки")

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'