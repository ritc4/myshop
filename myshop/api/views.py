from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer, OrderItemPickingSerializer
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
from rest_framework import status as drf_status
from django.contrib.auth import get_user_model


User = get_user_model()

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

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     user = self.request.user
    #     if not user.is_staff:
    #         qs = qs.filter(email=user.email)  # Фильтр для не-админов: только свои заказы
    #     return qs


    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     user = self.request.user
    #     status_param = self.request.query_params.get('status')

    #     # Админ: все заказы
    #     if user.is_staff:
    #         if status_param:
    #             qs = qs.filter(status=status_param)
    #         return qs

    #     # Сборщик: по умолчанию только 'obrabotka'
    #     if getattr(user, 'is_picker', False):
    #         return qs.filter(status='obrabotka')


    #     # Обычный пользователь: только свои заказы
    #     qs = qs.filter(email=user.email)
    #     if status_param:
    #         qs = qs.filter(status=status_param)
    #     return qs



    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        status_param = self.request.query_params.get('status')

        # Админ: все заказы
        if user.is_staff:
            if status_param:
                qs = qs.filter(status=status_param)
            return qs

        # Сборщик: только свои назначенные заказы, обычно со статусом 'obrabotka'
        if getattr(user, 'is_picker', False):
            qs = qs.filter(assigned_to=user)
            if status_param:
                qs = qs.filter(status=status_param)
            else:
                qs = qs.filter(status='obrabotka')  # по умолчанию только "в обработке"
            return qs

        # Обычный пользователь: только свои заказы по email
        qs = qs.filter(email=user.email)
        if status_param:
            qs = qs.filter(status=status_param)
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



class UpdateOrderItemPickingView(APIView):
    """
    Обновление складских полей по одной позиции заказа.
    Доступ: админ или посредник (is_picker).
    Также учитывается OrderPermission: сборщик видит только 'obrabotka'. 
    """
    permission_classes = [IsAuthenticated]  # базовая проверка 

    def post(self, request, order_id, item_id):
        # Сначала достаём заказ с учётом вашей логики доступа
        order = get_object_or_404(Order.objects.all(), pk=order_id)

        # Дополнительно прогоняем через OrderPermission, как в вьюсете
        perm = OrderPermission()
        if not perm.has_permission(request, self) or not perm.has_object_permission(request, self, order):
            return Response(
                {"detail": "Недостаточно прав для доступа к заказу."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        user = request.user
        # Разрешаем изменять только админу или посреднику
        if not (user.is_staff or getattr(user, 'is_picker', False)):
            return Response(
                {"detail": "Недостаточно прав для изменения позиций заказа."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        # Ищем нужную позицию в этом заказе
        try:
            item = order.items.get(pk=item_id)
        except OrderItem.DoesNotExist:
            return Response(
                {"detail": "Позиция не найдена в этом заказе."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        serializer = OrderItemPickingSerializer(
            item,
            data=request.data,
            partial=True,  # можно передавать только нужные поля
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=drf_status.HTTP_200_OK)
        return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)
    



class AssignOrderToPickerView(APIView):
    """
    Назначить заказ конкретному сборщику (picker).
    Доступ: только staff / admin.
    POST /api/v1/order//assign/
    Body: {"picker_id": 7}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user

        # только staff/admin
        if not user.is_staff:
            return Response(
                {"detail": "Нет прав назначать заказы."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        # находим заказ
        order = get_object_or_404(Order.objects.all(), pk=order_id)

        picker_id = request.data.get('picker_id')
        if not picker_id:
            return Response(
                {"detail": "Нужно передать picker_id."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        try:
            picker = User.objects.get(pk=picker_id, is_picker=True)
        except User.DoesNotExist:
            return Response(
                {"detail": "Сборщик с таким id не найден или не является сборщиком."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        order.assigned_to = picker
        # по желанию: сразу переводим в статус 'obrabotka'
        if order.status == 'new':
            order.status = 'obrabotka'
        # order.save(update_fields=['assigned_to', 'status'])
        order.save(update_fields=['assigned_to'])

        return Response(
            {"detail": f"Заказ назначен пользователю {picker.username}."},
            status=drf_status.HTTP_200_OK
        )
    


class TakeOrderView(APIView):
    """
    Сборщик сам берет себе свободный заказ.
    POST /api/v1/order//take/
    Доступ: только is_picker, плюс проверка OrderPermission.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user

        # только сборщик
        if not getattr(user, 'is_picker', False):
            return Response(
                {"detail": "Только посредник/сборщик может брать заказы в работу."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        # достаём заказ
        order = get_object_or_404(Order.objects.all(), pk=order_id)

        # проверяем доступ к заказу через твой OrderPermission
        perm = OrderPermission()
        if not perm.has_permission(request, self) or not perm.has_object_permission(request, self, order):
            return Response(
                {"detail": "Недостаточно прав для доступа к заказу."},
                status=drf_status.HTTP_403_FORBIDDEN
            )

        # заказ уже назначен другому пользователю
        if order.assigned_to is not None and order.assigned_to_id != user.id:
            return Response(
                {"detail": "Заказ уже назначен другому пользователю."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # по бизнес‑логике: какие статусы можно брать
        if order.status not in ['new', 'obrabotka']:
            return Response(
                {"detail": f"Нельзя взять заказ со статусом '{order.status}'."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        # назначаем на текущего пользователя
        order.assigned_to = user
        if order.status == 'new':
            order.status = 'obrabotka'
        order.save(update_fields=['assigned_to', 'status'])

        return Response(
            {"detail": "Заказ взят в работу."},
            status=drf_status.HTTP_200_OK
        )