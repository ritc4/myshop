from django.urls import path
from .views import cart_views

app_name = 'cart'

urlpatterns = [
    path('', cart_views, name='cart'),
    ]