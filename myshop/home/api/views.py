# from rest_framework import generics
# from .serializers import ProductSerializer, CategorySerializer
# from .pagination import StandardPagination
# from ..models import Product,Category
# from rest_framework import viewsets


# # class ProductListView(generics.ListAPIView):
# #     queryset = Product.objects.filter(is_hidden=False).prefetch_related(
# #         'product_prices__size'  # Предзагрузка для sizes_and_prices (избегает N+1)
# #     ).select_related('category')  # Предзагрузка для вложенной category
# #     serializer_class = ProductSerializer
# #     pagination_class = StandardPagination

# # class ProductDetailView(generics.RetrieveAPIView):
# #     queryset = Product.objects.filter(is_hidden=False).prefetch_related(
# #         'product_prices__size'  # То же для детального вида
# #     ).select_related('category')
# #     serializer_class = ProductSerializer



# # class CategoryListView(generics.ListAPIView):
# #     serializer_class = CategorySerializer
# #     queryset = Category.objects.all()
# #     pagination_class = StandardPagination



# class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = CategorySerializer
#     queryset = Category.objects.all()
#     pagination_class = StandardPagination



# class ProductViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Product.objects.filter(is_hidden=False).prefetch_related(
#             'product_prices__size'
#         ).select_related('category')
#     serializer_class = ProductSerializer
#     pagination_class = StandardPagination



from rest_framework import generics
from .serializers import ProductSerializer, CategorySerializer
from .pagination import StandardPagination
from ..models import Product, Category, ProductPrice, Size
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser  # Изменено: теперь IsAdminUser для ограничения доступа только админам


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')  # Добавлено: сортировка по name для алфавитного порядка в MPTT-дереве
    pagination_class = StandardPagination

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_hidden=False).prefetch_related(
        'product_prices__size'
    ).select_related('category')
    serializer_class = ProductSerializer
    pagination_class = StandardPagination

# Создание продукта с ценами и размерами (аналог ProductEnrollView, но для создания)
class CreateProductView(APIView):
    permission_classes = [IsAdminUser]  # Изменено: только админы могут создавать

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()  # Создаёт продукт
            # Ручная обработка nested product_prices (если сериализатор не nested)
            prices_data = request.data.get('product_prices', [])
            for price_data in prices_data:
                size_id = price_data.get('size')
                price_value = price_data.get('price')
                if size_id and price_value:
                    size = get_object_or_404(Size, pk=size_id)
                    ProductPrice.objects.create(product=product, size=size, price=price_value)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Обновление продукта с ценами и размерами (аналог ProductEnrollView, но для обновления)
class UpdateProductView(APIView):
    permission_classes = [IsAdminUser]  # Изменено: только админы могут обновлять

    def put(self, request, pk, format=None):
        product = get_object_or_404(Product, pk=pk, is_hidden=False)  # Только видимые продукты
        serializer = ProductSerializer(product, data=request.data, partial=True)  # partial=True для частичных обновлений
        if serializer.is_valid():
            product = serializer.save()
            # Ручная обработка nested: удалить старые цены и создать новые (для простоты; можно обновить существующие)
            product.product_prices.all().delete()  # Удалить старые
            prices_data = request.data.get('product_prices', [])
            for price_data in prices_data:
                size_id = price_data.get('size')
                price_value = price_data.get('price')
                if size_id and price_value:
                    size = get_object_or_404(Size, pk=size_id)
                    ProductPrice.objects.create(product=product, size=size, price=price_value)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Удаление продукта (аналог ProductEnrollView, но для удаления)
class DeleteProductView(APIView):
    permission_classes = [IsAdminUser]  # Изменено: только админы могут удалять

    def delete(self, request, pk, format=None):
        product = get_object_or_404(Product, pk=pk, is_hidden=False)  # Только видимые продукты
        product.delete()  # Каскадно удалит цены, если настроено в модели
        return Response({'deleted': True}, status=status.HTTP_204_NO_CONTENT)

# Создание категории (простая, без nested)
class CreateCategoryView(APIView):
    permission_classes = [IsAdminUser]  # Изменено: только админы могут создавать

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Обновление категории (простая, без nested)
class UpdateCategoryView(APIView):
    permission_classes = [IsAdminUser]  # Изменено: только админы могут обновлять

    def put(self, request, pk, format=None):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Удаление категории (простая, без nested)
class DeleteCategoryView(APIView):
    permission_classes = [IsAdminUser]  # Изменено: только админы могут удалять

    def delete(self, request, pk, format=None):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({'deleted': True}, status=status.HTTP_204_NO_CONTENT)



