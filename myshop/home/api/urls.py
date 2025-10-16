from django.urls import include,path
from .views import (
    ProductViewSet, 
    CategoryViewSet,
    CreateProductView, 
    UpdateProductView, 
    DeleteProductView,
    CreateCategoryView,  # Если нужен CRUD для категорий
    UpdateCategoryView,
    DeleteCategoryView,
    ) #ProductListView, ProductDetailView, CategoryListView,

from rest_framework import routers

app_name = 'product'


router = routers.DefaultRouter()
router.register('product', ProductViewSet)
router.register('category', CategoryViewSet)

urlpatterns = [
        
        path('', include(router.urls)),

        # Новые кастомные маршруты для продуктов (с nested ценами/размерами)
        path('products/create/', CreateProductView.as_view(), name='create-product'),
        path('products/update/<int:pk>/', UpdateProductView.as_view(), name='update-product'),
        path('products/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
        
        # Новые кастомные маршруты для категорий (если нужен CRUD)
        path('categories/create/', CreateCategoryView.as_view(), name='create-category'),
        path('categories/update/<int:pk>/', UpdateCategoryView.as_view(), name='update-category'),
        path('categories/delete/<int:pk>/', DeleteCategoryView.as_view(), name='delete-category'),

        ]