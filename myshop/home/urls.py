from django.urls import path
from .views import HomeView,ProductDetailView,ReviewsView,ContactsView,DeliveryView,NewsListView,ProductListView,SizeTableListView,Search
from django.views.decorators.cache import cache_page

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<str:slug>/', ProductListView.as_view(), name='category'),
    path('<int:id>/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('reviews/', ReviewsView.as_view(), name='reviews'),
    # path('contacts/', cache_page(3600)(ContactsView.as_view()), name='contacts'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    # path('delivery/', cache_page(3600)(DeliveryView.as_view()), name='delivery'),
    path('delivery/', DeliveryView.as_view(), name='delivery'),
    # path('news/', cache_page(600)(NewsListView.as_view()), name='news'),
    path('news/', NewsListView.as_view(), name='news'),
    # path('size_table/', cache_page(3600)(SizeTableListView.as_view()), name='size_table'),
    path('size_table/', SizeTableListView.as_view(), name='size_table'),
    path('search/', Search.as_view(), name='search'),
    ]