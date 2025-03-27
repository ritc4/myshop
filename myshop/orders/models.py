from django.db import models
from home.models import Product,Size,ProductPrice
from django_ckeditor_5.fields import CKEditor5Field
from decimal import Decimal
from django.core.validators import RegexValidator
from django.urls import reverse_lazy



class DeliveryMethod(models.Model):
    title = models.CharField(max_length=255, verbose_name="Способ доставки", db_index=True)

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


    first_name_last_name = models.CharField(max_length=255, verbose_name="Фамилия Имя Отчество", db_index=True) 
    email = models.EmailField(verbose_name="Электронная почта", db_index=True)
    phone = models.CharField(
        max_length=20,  # Увеличьте длину для учета пробелов и символов
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r'^(?:\+7|8)\s*\(?\d{3}\)?\s*\d{3}-\d{2}-\d{2}$|^(?:\+7|8)\d{10}$',  # Учитывает формат с 8 и +7
                message='Телефон должен быть в формате: +7 (XXX) XXX-XX-XX, 8 (XXX) XXX-XX-XX, +7XXXXXX или 8XXXXXXXXXX, где X - цифры.'
            )
        ]
    , db_index=True)
    
    
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
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    my_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий, скрытый от покупателя")
    created = models.DateTimeField(auto_now_add=True, db_index=True) 
    updated = models.DateTimeField(auto_now=True) 
    paid = models.BooleanField(default=False, verbose_name="Товар Оплачен", db_index=True)
    zamena_product = models.BooleanField(default=True, verbose_name="Предлагать замену товара")
    strahovat_gruz = models.BooleanField(default=True, verbose_name="Застраховать груз")
    soglasie_na_obrabotku_danyh = models.BooleanField(default=True,blank=False, verbose_name="Согласие на обработку персональных данных")
    soglasie_na_uslovie_sotrudnichestva = models.BooleanField(default=True,blank=False, verbose_name="Согласие с условиями сотрудничества")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='new',verbose_name="Статус заказа", db_index=True)
    delivery_method = models.ForeignKey(DeliveryMethod, blank=False,on_delete=models.SET_NULL, null=True, verbose_name="Способ доставки", db_index=True)
    price_delivery = models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True, verbose_name="Цена доставки", db_index=True)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Скидка", db_index=True)


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
    get_total_cost.short_description = 'Общая стоимость'


    def get_total_zakup_cost(self):
        total_zakup_cost = 0

        # Предварительная загрузка всех элементов и связанных объектов
        items = self.items.select_related('size').prefetch_related('size__product_size')

        for item in items:
            if item.size:  # Проверяем, что размер существует
                # Получаем все закупочные цены для текущего размера
                for price in item.size.product_size.all():
                    print(f"Закупочная цена для размера '{item.size.title}': {price.zacup_price}")
                    total_zakup_cost += price.zacup_price * item.quantity  # Учитываем количество

        return total_zakup_cost
    get_total_zakup_cost.short_description = 'Общая закупочная стоимость'


    
    def get_article_numbers(self):
        return [item.product.article_number for item in self.items.all() if item.product.article_number]
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE, db_index=True) 
    product = models.ForeignKey(Product,related_name='order_items', on_delete=models.CASCADE,verbose_name="Название товара", db_index=True) 
    price = models.DecimalField(max_digits=10,decimal_places=0, verbose_name="Цена", db_index=True) 
    quantity = models.PositiveIntegerField(default=1,verbose_name="Количество", db_index=True)
    # size = models.CharField(max_length=50, verbose_name="Размер", blank=True, null=True)  # Поле для размера
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, verbose_name="Размер", db_index=True)  # Изменено на ForeignKey
    
    
    def __str__(self):
        return str(self.product.title) 
    

    def get_cost(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0  # Возвращаем 0, если одно из значений отсутствует
    get_cost.short_description = 'Общая стоимость'  # Заголовок столбца

      
    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('amount', 'Скидка в рублях'),
        ('percentage', 'Скидка в %'),
    ]

    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name="Тип скидки", db_index=True)
    discount_value = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Размер скидки", db_index=True)

    def __str__(self):
        if self.discount_type == 'amount':
            return f'{self.discount_value} руб.'
        elif self.discount_type == 'percentage':
            return f'{self.discount_value} %'
        return 'Неизвестный тип скидки'
    

    class Meta:
        verbose_name = 'Скидка для клиента'
        verbose_name_plural = 'Скидки для клиентов'
