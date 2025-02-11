from django.urls import path
from .views import home,product_detail,registration,login,checkout,reviews,conditions,contacts,delivery,news,product_list

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('category/<str:slug>/', product_list, name='category'),
    path('<int:id>/<slug:slug>/', product_detail, name='product_detail'),
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('checkout/', checkout, name='checkout'),
    path('reviews/', reviews, name='reviews'),
    path('conditions/', conditions, name='conditions'),
    path('contacts/', contacts, name='contacts'),
    path('delivery/', delivery, name='delivery'),
    path('news/', news, name='news'),
    ]