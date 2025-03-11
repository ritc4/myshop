from django.urls import path
from .views import HomeView,ProductDetailView,ReviewsView,ContactsView,DeliveryView,NewsListView,ProductListView,SizeTableListView

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<str:slug>/', ProductListView.as_view(), name='category'),
    path('<int:id>/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('reviews/', ReviewsView.as_view(), name='reviews'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('delivery/', DeliveryView.as_view(), name='delivery'),
    path('news/', NewsListView.as_view(), name='news'),
    path('size_table/', SizeTableListView.as_view(), name='size_table'),
    ]