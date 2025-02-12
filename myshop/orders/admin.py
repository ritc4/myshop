from django.contrib import admin
from .models import Order, OrderItem 



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
 
 
 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'delivery', 
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
