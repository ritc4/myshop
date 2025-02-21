from django.contrib import admin
from .models import Order, OrderItem,DeliveryMethod



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    fields = ['product_image','product_article_number','product', 'product_size','product_mesto','product_zacup_price','quantity', 'price',]  # Добавьте поле product_image
    readonly_fields = ['product_image','product_article_number','product_size','product_mesto','product_zacup_price',]  # Убедитесь, что это поле только для чтения

    def product_article_number(self, obj):
        return obj.product_article_number()  # Вызов метода product_image из модели
    
    def product_image(self, obj):
        return obj.product_image()  # Вызов метода product_image из модели
    
    def product_size(self, obj):
        return obj.product_size()  # Вызов метода product_image из модели
    
    def product_mesto(self, obj):
        return obj.product_mesto()  # Вызов метода product_image из модели
    
    def product_mesto(self, obj):
        return obj.product_mesto()  # Вызов метода product_image из модели
    
    def product_zacup_price(self, obj):
        return obj.product_zacup_price()  # Вызов метода product_image из модели
 
 
 
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
        
    ]
    list_filter = ['paid', 'created', 'updated'] 
    inlines = [OrderItemInline]





@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display =[
        'title',
        ]

