from django.contrib import admin
from .models import Order, OrderItem,DeliveryMethod



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
 
 
 
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
        'updated'
    ]
    list_filter = ['paid', 'created', 'updated'] 
    inlines = [OrderItemInline]


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display =[
        'title',
        ]

