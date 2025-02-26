from django.db import models
from home.models import Product
from django.utils.safestring import mark_safe



class DeliveryMethod(models.Model):
    title = models.CharField(max_length=255, verbose_name="Способ доставки")

    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'

    def __str__(self):
        return self.title




class Order(models.Model):
    delivery_method = models.ForeignKey(DeliveryMethod, blank=False,on_delete=models.SET_NULL, null=True, verbose_name="Способ доставки")
    first_name_last_name = models.CharField(max_length=255, verbose_name="Фамилия Имя Отчество") 
    email = models.EmailField(verbose_name="Электронная почта")
    phone = models.CharField(max_length=12, verbose_name="Телефон")
    region = models.CharField(max_length=250, verbose_name="Регион")
    city = models.CharField(max_length=100, verbose_name="Город")
    address = models.CharField(max_length=250, verbose_name="Адрес") 
    passport_number = models.CharField(max_length=50, verbose_name="Паспортные данные",blank=True,null=True)
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 
    paid = models.BooleanField(default=False, verbose_name="Товар Оплачен")
    zamena_product = models.BooleanField(default=True, verbose_name="Предлагать замену товара")
    strahovat_gruz = models.BooleanField(default=True, verbose_name="Застраховать груз")


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created'] 
        indexes = [
            models.Index(fields=['-created']), 
        ]
    
    def __str__(self):
        return f"Заказ №{self.id} от {self.first_name_last_name}"
    
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    
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