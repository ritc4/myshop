from django.urls import path
from .views import home,product_detail,registration,login,reviews,contacts,delivery,news,ProductListView,size_table

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('category/<str:slug>/', ProductListView.as_view(), name='category'),
    path('<int:id>/<slug:slug>/', product_detail, name='product_detail'),
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('reviews/', reviews, name='reviews'),
    path('contacts/', contacts, name='contacts'),
    path('delivery/', delivery, name='delivery'),
    path('news/', news, name='news'),
    path('size_table/', size_table, name='size_table'),
    ]