from django.urls import path
from .views import home,get_category,product,registration,login,cart,checkout,reviews,conditions,contacts,delivery,news
from django.conf import settings
from django.conf.urls.static import static

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('category/<str:slug>/', get_category, name='category'),
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
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)