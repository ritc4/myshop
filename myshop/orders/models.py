from django.db import models
from home.models import Product
from django.utils.safestring import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import RegexValidator
from django.urls import reverse_lazy



class DeliveryMethod(models.Model):
    title = models.CharField(max_length=255, verbose_name="Способ доставки")

    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'

    def __str__(self):
        return f"{self.title}"



class Order(models.Model):

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('obrabotka', 'В обработке'),
        ('oplata', 'Ожидает оплаты'),
        ('assembled', 'Собран'),
        ('canceled', 'Отменен'),
        ('pending', 'В ожидании'),
    ]


    first_name_last_name = models.CharField(max_length=255, verbose_name="Фамилия Имя Отчество") 
    email = models.EmailField(verbose_name="Электронная почта")
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
    passport_number = models.CharField(
        max_length=15,
        verbose_name="Паспортные данные",
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\d{10}$',  # Регулярное выражение для 10 цифр
            message='Паспортные данные должны состоять из 10 цифр.'
        )])
    comment = CKEditor5Field(config_name='extends',blank=True, null=True, verbose_name="Комментарий")
    my_comment = CKEditor5Field(config_name='extends',blank=True, null=True, verbose_name="Комментарий, скрытый от покупателя")
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 
    paid = models.BooleanField(default=False, verbose_name="Товар Оплачен")
    zamena_product = models.BooleanField(default=True, verbose_name="Предлагать замену товара")
    strahovat_gruz = models.BooleanField(default=True, verbose_name="Застраховать груз")
    soglasie_na_obrabotku_danyh = models.BooleanField(default=True,blank=False, verbose_name="Согласие на обработку персональных данных")
    soglasie_na_uslovie_sotrudnichestva = models.BooleanField(default=True,blank=False, verbose_name="Согласие с условиями сотрудничества")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='new',verbose_name="Статус заказа")
    delivery_method = models.ForeignKey(DeliveryMethod, blank=False,on_delete=models.SET_NULL, null=True, verbose_name="Способ доставки")
    price_delivery = models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True, verbose_name="Цена доставки")
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Скидка")


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created'] 
        indexes = [
            models.Index(fields=['-created']), 
        ]
    
    def __str__(self):
        return f"Заказ №{self.id} от {self.first_name_last_name}"
    

    def get_absolute_url(self):
        return reverse_lazy("users:order_detail", kwargs={"pk":self.pk})
    
    


    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())

        # Проверяем, есть ли способ доставки и установлена ли цена доставки
        if self.delivery_method and self.price_delivery is not None:
            total_cost += self.price_delivery

        # Отладка: выводим общую стоимость перед применением скидки
        print(f"Общая стоимость до применения скидки: {total_cost}")

        # Применяем скидку, если она есть
        if self.discount:
            print(f"Скидка найдена: {self.discount.discount_value}, Тип: {self.discount.discount_type}")
            if self.discount.discount_type == 'amount':
                discount_value = round(Decimal(self.discount.discount_value))  # Округляем до целого
                total_cost -= discount_value  # Скидка в рублях
                print(f"Применена скидка в рублях: {discount_value}")
            elif self.discount.discount_type == 'percentage':
                discount_value = round(total_cost * (Decimal(self.discount.discount_value) / 100))  # Округляем до целого
                total_cost -= discount_value
                print(f"Применена скидка в процентах: {self.discount.discount_value}% (сумма: {discount_value})")
        else:
            print("Скидка не найдена.")

        return max(total_cost, 0)  # Обеспечиваем, чтобы стоимость не была отрицательной
    




    def get_total_zakup_cost(self):
        total_zakup_cost = 0
        for item in self.items.all():
            # Получаем все цены для текущего продукта
            product_prices = item.product.product_prices.all()  # Получаем все связанные ProductPrice
            if product_prices.exists():
                # Получаем первую цену (или используйте другую логику для выбора нужной цены)
                zacup_price = product_prices.first().zacup_price
                total_zakup_cost += zacup_price * item.quantity  # Умножаем на количество
        return total_zakup_cost


    def get_article_numbers(self):
        return [item.product.article_number for item in self.items.all() if item.product.article_number]
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE) 
    product = models.ForeignKey(Product,related_name='order_items', on_delete=models.CASCADE,verbose_name="Название товара") 
    price = models.DecimalField(max_digits=10,decimal_places=0, verbose_name="Цена") 
    quantity = models.PositiveIntegerField(default=1,verbose_name="Количество")
    size = models.CharField(max_length=50, verbose_name="Размер", blank=True, null=True)  # Поле для размера


    def __str__(self):
        return str(self.product.title) 
    

    def get_cost(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0  # Возвращаем 0, если одно из значений отсутствует

    
    def product_article_number(self):
        return self.product.article_number
    
    def product_mesto(self):
        return self.product.mesto
    
    def product_zacup_price(self):
        # Получаем все цены для текущего продукта
        product_prices = self.product.product_prices.all()  # Получаем все связанные ProductPrice
        if product_prices.exists():
            return product_prices.first().zacup_price  # Возвращаем первую цену
        return None  # Если цен нет, возвращаем None
    
    
    def product_image(self):
        # Получаем первое изображение, если оно существует
        first_image = self.product.images.first()  # Здесь используем related_name 'images'
        if first_image:
            return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
        else:
            return 'Нет фото'

    product_image.short_description = 'Фото товара'

      
    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('amount', 'Скидка в рублях'),
        ('percentage', 'Скидка в %'),
    ]

    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name="Тип скидки")
    discount_value = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Размер скидки")

    def __str__(self):
        if self.discount_type == 'amount':
            return f'{self.discount_value} руб.'
        elif self.discount_type == 'percentage':
            return f'{self.discount_value} %'
        return 'Неизвестный тип скидки'
    

    class Meta:
        verbose_name = 'Скидка для клиента'
        verbose_name_plural = 'Скидки для клиентов'
