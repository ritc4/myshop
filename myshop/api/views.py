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
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
from .pagination import StandardPagination
from home.models import Product, Category, ProductPrice, Size, ProductImage  # Добавлен ProductImage
from orders.models import Order
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser  # Изменено: теперь IsAdminUser для ограничения доступа только админам
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser  # Добавлено для обработки файлов
import json

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]  # Включает поиск (можно добавить OrderingFilter для сортировки)
    search_fields = ['id','name', 'slug', 'parent_id']

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_hidden=False).prefetch_related(
        'product_prices__size', 'images'  # Добавлено prefetch для изображений
    ).select_related('category')
    serializer_class = ProductSerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]  # Включает поиск (можно добавить OrderingFilter для сортировки)
    search_fields = ['id','title', 'slug', 'article_number', 'mesto',]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items__product', 'items__size','delivery_method')  # Оптимизация, как в ваших views
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]  # Включает поиск (можно добавить OrderingFilter для сортировки)
    search_fields = ['id', 'first_name_last_name', 'address', 'status', 'email', 'phone']
    ordering = ['-created']


# Создание продукта с ценами, размерами и изображениями
class CreateProductView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  # Исправлено: FormParser вместо JSONParser для mixed data (поля + файлы)
    
    def post(self, request):
        # print(f"DEBUG: request.FILES = {request.FILES}")  # Дебаг: посмотрите в консоли Django, приходят ли файлы
        data = request.data.copy()
        
        # Валидация product_prices (без изменений)
        product_prices_data = data.get('product_prices')
        if not product_prices_data:
            return Response({"error": "product_prices обязательно"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product_prices = json.loads(product_prices_data)
        except json.JSONDecodeError:
            return Response({"error": "product_prices должно быть валидным JSON"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(product_prices, list):
            return Response({"error": "product_prices должно быть списком"}, status=status.HTTP_400_BAD_REQUEST)
        
        for pp in product_prices:
            if not isinstance(pp, dict):
                return Response({"error": "Каждый элемент product_prices должен быть объектом"}, status=status.HTTP_400_BAD_REQUEST)
            if 'size' not in pp or 'price' not in pp or 'zacup_price' not in pp:
                return Response({"error": "size, price и zacup_price обязательны для каждого product_price"}, status=status.HTTP_400_BAD_REQUEST)
            # Дополнительная валидация: price и zacup_price должны быть числами
            try:
                pp['price'] = float(pp['price'])
                pp['zacup_price'] = float(pp['zacup_price'])
                if 'old_price' in pp:
                    old_price = pp['old_price']
                    pp['old_price'] = float(old_price) if old_price is not None else None
            except (ValueError, TypeError):
                return Response({"error": "price, zacup_price и old_price должны быть числами"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Создаём продукт через сериализатор (без product_prices)
        product_data = data.copy()
        if 'product_prices' in product_data:
            del product_data['product_prices']  # Убираем, чтобы сериализатор не жаловался
        product_serializer = ProductSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = product_serializer.save()
        
        # Обрабатываем product_prices с созданием размера на лету (без изменений)
        for pp in product_prices:
            size_value = pp['size']
            price = pp['price']
            zacup_price = pp['zacup_price']
            old_price = pp.get('old_price')
            
            # Логика для size: строка (новый) или int (ID существующего)
            if isinstance(size_value, str):
                # Ищем по title (case-sensitive, но можно добавить .lower() если нужно)
                size_obj, created = Size.objects.get_or_create(title=size_value)
                # if created:
                    # print(f"Создан новый размер: {size_value} (ID: {size_obj.id})")  # Для дебага
            elif isinstance(size_value, int):
                try:
                    size_obj = Size.objects.get(id=size_value)
                except Size.DoesNotExist:
                    return Response({"error": f"Размер с ID {size_value} не найден"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "size должно быть строкой (новый размер) или числом (ID)"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Создаём ProductPrice
            ProductPrice.objects.create(
                product=product,
                size=size_obj,
                price=price,
                zacup_price=zacup_price,
                old_price=old_price
            )
        
        # Обрабатываем изображения (ручная, как раньше)
        if 'images' in request.FILES:
            # print(f"DEBUG: Загружаем {len(request.FILES.getlist('images'))} изображений")  # Дебаг
            for image_file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=image_file)
                # print(f"DEBUG: Сохранено: {image_file.name}")  # Дебаг
        
        # Возвращаем полный продукт с sizes_and_prices
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateProductView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  # Исправлено: FormParser вместо JSONParser
    
    def put(self, request, pk):
        # print(f"DEBUG: request.FILES = {request.FILES}")  # Дебаг
        product = get_object_or_404(Product, pk=pk)
        data = request.data.copy()
        
        # Валидация product_prices (только если переданы, без изменений)
        product_prices_data = data.get('product_prices')
        if product_prices_data:
            try:
                product_prices = json.loads(product_prices_data)
            except json.JSONDecodeError:
                return Response({"error": "product_prices должно быть валидным JSON"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(product_prices, list):
                return Response({"error": "product_prices должно быть списком"}, status=status.HTTP_400_BAD_REQUEST)
            
            for pp in product_prices:
                if not isinstance(pp, dict):
                    return Response({"error": "Каждый элемент product_prices должен быть объектом"}, status=status.HTTP_400_BAD_REQUEST)
                if 'size' not in pp or 'price' not in pp or 'zacup_price' not in pp:
                    return Response({"error": "size, price и zacup_price обязательны для каждого product_price"}, status=status.HTTP_400_BAD_REQUEST)
                # Валидация чисел (как в create)
                try:
                    pp['price'] = float(pp['price'])
                    pp['zacup_price'] = float(pp['zacup_price'])
                    if 'old_price' in pp:
                        old_price = pp['old_price']
                        pp['old_price'] = float(old_price) if old_price is not None else None
                except (ValueError, TypeError):
                    return Response({"error": "price, zacup_price и old_price должны быть числами"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Обновляем продукт через сериализатор (partial=True для PUT/PATCH)
        product_data = data.copy()
        if 'product_prices' in product_data:
            del product_data['product_prices']
        product_serializer = ProductSerializer(product, data=product_data, partial=True)
        if not product_serializer.is_valid():
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = product_serializer.save()
        
        # Если переданы product_prices, удаляем старые и создаём новые (без изменений)
        if product_prices_data:
            product.product_prices.all().delete()  # Удаляем старые цены
            for pp in product_prices:
                size_value = pp['size']
                price = pp['price']
                zacup_price = pp['zacup_price']
                old_price = pp.get('old_price')
                
                # Та же логика для size
                if isinstance(size_value, str):
                    size_obj, created = Size.objects.get_or_create(title=size_value)
                    # if created:
                        # print(f"Создан новый размер: {size_value} (ID: {size_obj.id})")
                elif isinstance(size_value, int):
                    try:
                        size_obj = Size.objects.get(id=size_value)
                    except Size.DoesNotExist:
                        return Response({"error": f"Размер с ID {size_value} не найден"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "size должно быть строкой или числом"}, status=status.HTTP_400_BAD_REQUEST)
                
                ProductPrice.objects.create(
                    product=product,
                    size=size_obj,
                    price=price,
                    zacup_price=zacup_price,
                    old_price=old_price
                )
        
        # Обрабатываем изображения (удаляем старые, если новые переданы)
        if 'images' in request.FILES:
            # print(f"DEBUG: Обновляем {len(request.FILES.getlist('images'))} изображений")  # Дебаг
            product.images.all().delete()  # Предполагаю, что images — related_name для ProductImage
            for image_file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=image_file)
                # print(f"DEBUG: Сохранено: {image_file.name}")
        
        # Возвращаем обновлённый продукт
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Удаление продукта (без изменений)
class DeleteProductView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk, format=None):
        product = get_object_or_404(Product, pk=pk, is_hidden=False)
        product.delete()
        return Response({'deleted': True}, status=status.HTTP_204_NO_CONTENT)

# Создание категории с изображением
class CreateCategoryView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, JSONParser]  # Уже есть (для категорий работает, так как сериализатор обрабатывает image)

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Обновление категории с изображением
class UpdateCategoryView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, JSONParser]  # Уже есть

    def put(self, request, pk, format=None):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Удаление категории (без изменений)
class DeleteCategoryView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        # Проверяем, есть ли связанные продукты
        if Product.objects.filter(category=category).exists():
            return Response(
                {"error": "Нельзя удалить категорию, так как у неё есть связанные продукты. Сначала удалите или переместите продукты."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Если нет связанных продуктов, удаляем категорию
        category.delete()
        return Response({'deleted': True}, status=status.HTTP_204_NO_CONTENT)










class UpdateOrderView(APIView):
    permission_classes = [IsAdminUser]  # Только админы
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related('items__product', 'items__size'), pk=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related('items__product', 'items__size'), pk=pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)  # partial=True для частичного обновления
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Ошибка при обновлении заказа: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteOrderView(APIView):
    permission_classes = [IsAdminUser]  # Только админы

    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        try:
            order.delete()
            return Response({"message": "Заказ удален"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Ошибка при удалении заказа: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)