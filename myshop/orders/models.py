from django.db import models
from home.models import Product,Size,ProductPrice
from django_ckeditor_5.fields import CKEditor5Field
from decimal import Decimal
from django.core.validators import RegexValidator
from django.urls import reverse_lazy
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings


class DeliveryMethod(models.Model):
    title = models.CharField(max_length=255, verbose_name="Способ доставки", db_index=True)
    is_hidden = models.BooleanField(default=False,verbose_name='Скрыть способ доставки',db_index=True)  # Поле для скрытия

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
        blank=True,
        null=True,
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
    delivery_method = models.ForeignKey(DeliveryMethod,blank=False,on_delete=models.SET_NULL, null=True, verbose_name="Способ доставки", db_index=True,limit_choices_to={'is_hidden': False})
    price_delivery = models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True, verbose_name="Цена доставки", db_index=True)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Скидка", db_index=True,limit_choices_to={'is_hidden': False})
    # НОВОЕ ПОЛЕ: кому назначен заказ (сборщик/посредник)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='assigned_orders',null=True,blank=True,on_delete=models.SET_NULL,verbose_name="Назначено (посредник/сборщик)",db_index=True,)


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['status', 'assigned_to']),
        ]
    
    def __str__(self):
        return f"Заказ №{self.id} от {self.first_name_last_name}"
    

    def get_absolute_url(self):
        return reverse_lazy("users:order_detail", kwargs={"pk":self.pk})
    

    # def get_total_cost(self):
    #     total_cost = sum(item.get_cost() for item in self.items.all())

    #     # Проверяем, есть ли способ доставки и установлена ли цена доставки
    #     if self.delivery_method and self.price_delivery is not None:
    #         total_cost += self.price_delivery

    #     # Отладка: выводим общую стоимость перед применением скидки
    #     print(f"Общая стоимость до применения скидки: {total_cost}")

    #     # Применяем скидку, если она есть
    #     if self.discount:
    #         print(f"Скидка найдена: {self.discount.discount_value}, Тип: {self.discount.discount_type}")
    #         if self.discount.discount_type == 'amount':
    #             discount_value = round(Decimal(self.discount.discount_value))  # Округляем до целого
    #             total_cost -= discount_value  # Скидка в рублях
    #             print(f"Применена скидка в рублях: {discount_value}")
    #         elif self.discount.discount_type == 'percentage':
    #             discount_value = round(total_cost * (Decimal(self.discount.discount_value) / 100))  # Округляем до целого
    #             total_cost -= discount_value
    #             print(f"Применена скидка в процентах: {self.discount.discount_value}% (сумма: {discount_value})")
    #     else:
    #         print("Скидка не найдена.")

    #     return max(total_cost, 0)  # Обеспечиваем, чтобы стоимость не была отрицательной
    # get_total_cost.short_description = 'Общая стоимость'



    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())

        # Проверяем, есть ли способ доставки и установлена ли цена доставки
        if self.delivery_method and self.price_delivery is not None:
            total_cost += self.price_delivery

        # Применяем скидку, если она есть
        if self.discount:
            if self.discount.discount_type == 'amount':
                discount_value = round(Decimal(self.discount.discount_value))  # Округляем до целого
                total_cost -= discount_value  # Скидка в рублях
            elif self.discount.discount_type == 'percentage':
                discount_value = round(total_cost * (Decimal(self.discount.discount_value) / 100))  # Округляем до целого
                total_cost -= discount_value

        return max(total_cost, 0)  # Обеспечиваем, чтобы стоимость не была отрицательной

    get_total_cost.short_description = 'Общая стоимость'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, db_index=True) 
    product_price = models.ForeignKey(ProductPrice, related_name='order_items', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='«Редактировать» или «Изменить» товар', db_index=True)
    product_snapshot = models.CharField(max_length=255, blank=True, null=True, verbose_name="Товар (архив)", db_index=True)
    size_snapshot = models.CharField(max_length=50, blank=True, null=True, verbose_name="Размер (архив)", db_index=True)
    zacup_price_snapshot = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="Закупочная цена (архив)", db_index=True)
    article_snapshot = models.CharField(max_length=100, blank=True, null=True, verbose_name="Артикул (архив)", db_index=True)  # Для article_number
    mesto_snapshot = models.CharField(max_length=100, blank=True, null=True, verbose_name="Место (архив)", db_index=True)  # Для mesto
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена продажи", db_index=True, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество", db_index=True, validators=[MinValueValidator(1)])
    is_price_custom = models.BooleanField(default=False, verbose_name="Редактировать цену")


    # что фактически собрали, информация по сборке товара от склада
    picked_quantity = models.PositiveIntegerField(blank=True, null=True,verbose_name="Фактическое количество (склад)", db_index=True)
    picked_zacup_price = models.DecimalField(max_digits=10, decimal_places=0,blank=True, null=True,verbose_name="Фактическая цена (склад)", db_index=True)
    picked_comment = models.CharField(max_length=255,blank=True,null=True,verbose_name="Комментарий склада",db_index=True,)
    is_picked = models.BooleanField(default=False,verbose_name="Позиция собрана (склад)", db_index=True)


    def save(self, *args, **kwargs):
        if self.product_price and not self.is_price_custom:
            self.price = self.product_price.price
            # Копируем snapshots, включая новые
            self.product_snapshot = self.product_price.product.title
            self.size_snapshot = self.product_price.size.title
            self.zacup_price_snapshot = self.product_price.zacup_price
            self.article_snapshot = self.product_price.product.article_number
            self.mesto_snapshot = self.product_price.product.mesto
        
        super().save(*args, **kwargs)

        
    # def __str__(self):
    #     return f"{self.product_price.product.title, self.product_price.product.id if self.product_price else 'Товар удалён или в архиве'}" 


    def __str__(self):
        try:
            title = self.product_price.product.title
            product_id = self.product_price.product.id
            return f"ID: {product_id}, Название: {title}"
        except AttributeError:
            return "Товар удалён или в архиве"



    def get_cost(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0  # Или self.product_price.price * self.quantity, если product_price выбран и !is_price_custom
    get_cost.short_description = 'Общая стоймость'


    def product_zacup_price(self): 
        """Возвращает закупочную цену для текущего размера товара (приоритет snapshot, fallback к актуальному)."""
        if self.zacup_price_snapshot is not None:
            return self.zacup_price_snapshot  # Используем архив
        elif self.product_price and self.product_price.zacup_price is not None:
            return self.product_price.zacup_price  # Fallback к актуальному
        return 0  # Или 'Нет цены' для consistency с другими методами, но как Decimal, лучше 0
    product_zacup_price.short_description = 'Закупочная цена (архив)' 


    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'
        unique_together = ['order', 'product_price']
        ordering = ['id']
        indexes = [
            models.Index(fields=['order', 'product_price'], name='orderitem_order_prodprice_idx'),
            models.Index(fields=['product_snapshot']),
            models.Index(fields=['size_snapshot']),
            models.Index(fields=['article_snapshot']),  # Новый индекс
            models.Index(fields=['mesto_snapshot']),    # Новый индекс
        ]
 
class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('amount', 'Скидка в рублях'),
        ('percentage', 'Скидка в %'),
    ]

    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name="Тип скидки", db_index=True)
    discount_value = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Размер скидки", db_index=True)
    is_hidden = models.BooleanField(default=False,verbose_name='Скрыть скидку',db_index=True)  # Поле для скрытия

    def __str__(self):
        if self.discount_type == 'amount':
            return f'{self.discount_value} руб.'
        elif self.discount_type == 'percentage':
            return f'{self.discount_value} %'
        return 'Неизвестный тип скидки'
    

    class Meta:
        verbose_name = 'Скидка для клиента'
        verbose_name_plural = 'Скидки для клиентов'
