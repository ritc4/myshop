from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
from .pagination import StandardPagination
from home.models import Product, Category, ProductPrice, Size, ProductImage  # Добавлен ProductImage
from orders.models import Order, OrderItem  # Добавлен OrderItem для работы с snapshots в заказах
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser  # Изменено: теперь IsAdminUser для ограничения доступа только админам
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser  # Добавлено для обработки файлов
import json
from .permissions import IsAdminOrAuthenticatedReadOnly, OrderPermission

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]
    queryset = Category.objects.select_related(
        'parent', 
        'parent__parent', 
        'parent__parent__parent', 
        'parent__parent__parent__parent'
    ).prefetch_related('children').all()
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]  # Включает поиск (можно добавить OrderingFilter для сортировки)
    search_fields = ['id','name', 'slug', 'parent_id']

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_hidden=False).select_related('category', 'category__parent').prefetch_related(
        'product_prices__size', 'images' 
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]  # Включает поиск (можно добавить OrderingFilter для сортировки)
    search_fields = ['id','title', 'slug', 'article_number', 'mesto',]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('delivery_method', 'discount').prefetch_related(
        'items__product_price__product',  # Изменено: items__product -> items__product_price__product
        'items__product_price__size',      # Изменено: items__size -> items__product_price__size
        'items__product_price__product__images'  # Изменено: для изображений теперь через product_price
    )
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]  # Включает поиск (можно добавить OrderingFilter для сортировки)
    search_fields = ['id', 'first_name_last_name', 'address', 'status', 'email', 'phone']
    ordering = ['-created']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(email=user.email)  # Фильтр для не-админов: только свои заказы
        return qs

    def get_serializer_context(self):
        # Удалена логика order_snapshots: snapshots теперь в полях OrderItem
        return super().get_serializer_context()


# Создание продукта с ценами, размерами и изображениями
class CreateProductView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  # Исправлено: FormParser вместо JSONParser для mixed data (поля + файлы)
    
    def post(self, request):
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
            for image_file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=image_file)
        
        # Возвращаем полный продукт с sizes_and_prices
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateProductView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  # Исправлено: FormParser вместо JSONParser
    
    def put(self, request, pk):
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
            product.images.all().delete()  # Предполагаю, что images — related_name для ProductImage
            for image_file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=image_file)
        
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
        order = get_object_or_404(Order.objects.prefetch_related('items__product_price__product', 'items__product_price__size'), pk=pk)
        # Удалена логика order_snapshots: snapshots в полях модели
        serializer = OrderSerializer(order)  # Нет необходимости в context
        return Response(serializer.data)


    def put(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related('items__product_price__product', 'items__product_price__size'), pk=pk)
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
