from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from orders.models import DeliveryMethod


class User(AbstractUser ):
    phone = models.CharField(
        max_length=20,  # Увеличьте длину для учета пробелов и символов
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r'^(?:\+7|8)\s*\(?\d{3}\)?\s*\d{3}-\d{2}-\d{2}$|^(?:\+7|8)\d{10}$',  # Учитывает формат с 8 и +7
                message='Телефон должен быть в формате: +7 (XXX) XXX-XX-XX, 8 (XXX) XXX-XX-XX, +7XXXXXX или 8XXXXXXXXXX, где X - цифры.'
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
                regex=r'^\d{6}$',  # Регулярное выражение для ровно 6 цифр
                message='Индекс должен состоять только из 6 цифр.'
            )
        ]
    )
    photo = models.ImageField(upload_to="users/%Y/%m/%d/",blank=True,null=True,verbose_name="Фотография")
    delivery_method = models.ForeignKey(DeliveryMethod, blank=False, on_delete=models.SET_NULL, null=True, verbose_name="Способ доставки")

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'