from django.urls import path
from .views import home,get_category,product_details,registration,login,checkout,reviews,conditions,contacts,delivery,news

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('category/<str:slug>/', get_category, name='category'),
    path('product/<str:slug>/', product_details, name='product'),
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('checkout/', checkout, name='checkout'),
    path('reviews/', reviews, name='reviews'),
    path('conditions/', conditions, name='conditions'),
    path('contacts/', contacts, name='contacts'),
    path('delivery/', delivery, name='delivery'),
    path('news/', news, name='news'),
    ]