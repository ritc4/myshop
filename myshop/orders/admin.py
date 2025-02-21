from django.contrib import admin
from .models import Order, OrderItem,DeliveryMethod
from django.utils.safestring import mark_safe



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    fields = ['product_image','product','product_article_number','size','product_mesto','product_zacup_price','quantity', 'price','get_cost',]  # Добавьте поле product_image
    readonly_fields = ['product_image','product_article_number','size','product_mesto','product_zacup_price','get_cost']  # Убедитесь, что это поле только для чтения

    
    def get_cost(self, obj):  # Добавляем obj как второй аргумент
        return obj.get_cost() if obj else 0  # Проверяем, что obj не равен None
    get_cost.short_description = 'Стоимость'  # Заголовок столбца
    
    
    def product_article_number(self, obj):
        return obj.product_article_number()  # Вызов метода product_image из модели
    product_article_number.short_description = 'Артикул'
    
    def product_image(self, obj):
        return obj.product_image()  # Вызов метода product_image из модели
    product_image.short_description = 'Фото'
    
    def product_mesto(self, obj):
        return obj.product_mesto()  # Вызов метода product_image из модели
    product_mesto.short_description = 'Место'
    
    def product_zacup_price(self, obj):
        return obj.product_zacup_price()  # Вызов метода product_image из модели  
    product_zacup_price.short_description = 'Закупочная цена'
    
 
 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'delivery_method', 
        'first_name_last_name',
        'email',
        'phone',
        'region',
        'city',
        'address',
        'comment',   
        'paid', 
        'created',
        'updated',
        'get_total_cost',
        
    ]
    
    
    list_filter = ['paid', 'created', 'updated'] 
    inlines = [OrderItemInline]

    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Общая стоимость'



@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display =[
        'title',
        ]

