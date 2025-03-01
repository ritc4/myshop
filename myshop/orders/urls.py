from django.urls import path 
from .views import order_create,admin_order_pdf
 
 
app_name = 'orders' 


urlpatterns = [
    path('create/', order_create, name='order_create'), 
    path('order/<int:order_id>/pdf/', admin_order_pdf,name='admin_order_pdf'),
]