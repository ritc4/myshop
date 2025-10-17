from django.urls import include,path
from .views import (
    ProductViewSet, 
    CategoryViewSet,
    OrderViewSet,
    CreateProductView, 
    UpdateProductView, 
    DeleteProductView,
    CreateCategoryView,  # Если нужен CRUD для категорий
    UpdateCategoryView,
    DeleteCategoryView,
    UpdateOrderView,
    DeleteOrderView
    )

from rest_framework import routers

app_name = 'product'


router = routers.DefaultRouter()
router.register('product', ProductViewSet)
router.register('category', CategoryViewSet)
router.register('order', OrderViewSet)


urlpatterns = [
        
        path('', include(router.urls)),

        path('categories/', CategoryViewSet.as_view({'get': 'list'}), name='category-list'),
        path('categories/create/', CreateCategoryView.as_view(), name='category-create'),
        path('categories/<int:pk>/update/', UpdateCategoryView.as_view(), name='category-update'),
        path('categories/<int:pk>/delete/', DeleteCategoryView.as_view(), name='category-delete'),

        # Для продуктов
        path('products/', ProductViewSet.as_view({'get': 'list'}), name='product-list'),
        path('products/create/', CreateProductView.as_view(), name='product-create'),
        path('products/<int:pk>/update/', UpdateProductView.as_view(), name='product-update'),
        path('products/<int:pk>/delete/', DeleteProductView.as_view(), name='product-delete'),


        path('order/<int:pk>/update/', UpdateOrderView.as_view(), name='update_order'),
        path('order/<int:pk>/delete/', DeleteOrderView.as_view(), name='delete_order'),

        ]