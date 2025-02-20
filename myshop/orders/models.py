from django.db import models
from home.models import Product



class DeliveryMethod(models.Model):
    title = models.CharField(max_length=255, verbose_name="Способ доставки")

    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'

    def __str__(self):
        return self.title




class Order(models.Model):
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.PROTECT, null=True, verbose_name="Способ доставки", blank=False,default=0)
    first_name_last_name = models.CharField(max_length=255, verbose_name="Фамилия Имя Отчество") 
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone = models.CharField(max_length=12, verbose_name="Телефон")
    region = models.CharField(max_length=250, verbose_name="Регион")
    city = models.CharField(max_length=100, verbose_name="Город")
    address = models.CharField(max_length=250, verbose_name="Адрес") 
    passport_number = models.CharField(max_length=50, verbose_name="Паспортные данные",blank=False,null=True)
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 
    paid = models.BooleanField(default=False, verbose_name="Товар Оплачен")
    zamena_product = models.BooleanField(default=True, verbose_name="Предлагать замену товара")
    strahovat_gruz = models.BooleanField(default=True, verbose_name="Застраховать груз")


    class Meta:
            ordering = ['-created'] 
            indexes = [
                models.Index(fields=['-created']), 
            ]

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f'Order {self.id}' 
    
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())



class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE) 
    product = models.ForeignKey(Product,related_name='order_items', on_delete=models.CASCADE,verbose_name="Название товара") 
    price = models.DecimalField(max_digits=10,decimal_places=2, verbose_name="Цена") 
    quantity = models.PositiveIntegerField(default=1,verbose_name="Количество")

    
    def __str__(self):
        return str(self.id) 


    def get_cost(self):
        return self.price * self.quantity
    
    
    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'