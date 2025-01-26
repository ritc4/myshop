from django.urls import path
from .views import home,category,product


app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('category/', category, name='category'),
    path('product/', product, name='product'),
    ]