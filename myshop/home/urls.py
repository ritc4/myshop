from django.urls import path
from .views import home,category,product,registration,login,cart,checkout,reviews,conditions,contacts,delivery,news


app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('category/', category, name='category'),
    path('product/', product, name='product'),
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('reviews/', reviews, name='reviews'),
    path('conditions/', conditions, name='conditions'),
    path('contacts/', contacts, name='contacts'),
    path('delivery/', delivery, name='delivery'),
    path('news/', news, name='news'),
    ]