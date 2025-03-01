from django.contrib import admin
from .models import Order, OrderItem,DeliveryMethod
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.urls import reverse


def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id]) 
    return mark_safe(f'<a href="{url}">Чек</a>')
order_pdf.short_description = 'Чеки'



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
        'get_total_zakup_cost',
         order_pdf, 
        ]
    
    list_editable = ['paid']
    readonly_fields = ['get_total_zakup_cost','get_total_cost']
    list_filter = ['paid', 'created', 'updated'] 
    inlines = [OrderItemInline]
    search_fields = ['items__product__article_number','first_name_last_name', 'email', 'phone',]  # Поля для поиска

    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Общая стоимость'


    def get_total_zakup_cost(self, obj):
        return obj.get_total_zakup_cost()
    get_total_zakup_cost.short_description = 'Общая закупочная стоимость'


    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(items__product__article_number__icontains=search_term) | 
                Q(first_name_last_name__icontains=search_term) | 
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            ).distinct()
        return super().get_search_results(request, queryset, search_term)


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display =[
        'title',
        ]

