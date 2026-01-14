from unidecode import unidecode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError  # Добавлено
from home.models import Category, Product, ProductImage, Size, ProductPrice  # Добавлен ProductPrice для прямого доступа
from orders.models import Order, OrderItem, DeliveryMethod, Discount
from django.utils.text import slugify
from django.utils.safestring import mark_safe

def generate_article_number():
    last_product = Product.objects.order_by('-article_number').first()
    if last_product:
        return last_product.article_number + 1
    return 1

def generate_unique_slug(title, article_number, exclude_pk=None):
    """
    Генерирует уникальный slug и article_number.
    Формат slug: slugified(title)-article_number.
    Если конфликт (slug или article_number), увеличивает article_number до уникальности.
    Возвращает (slug, corrected_article_number).
    """
    if not title or article_number is None:
        raise ValidationError("Название и артикул обязательны для генерации slug.")
    
    current_article = article_number
    max_attempts = 10000  # Лимит для избежания бесконечного цикла
    attempts = 0
    
    while attempts < max_attempts:
        base_slug = slugify(f"{unidecode(title)}-{current_article}")
        # Проверяем уникальность slug И article_number (исключая exclude_pk)
        slug_exists = Product.objects.filter(slug=base_slug).exclude(pk=exclude_pk).exists()
        article_exists = Product.objects.filter(article_number=current_article).exclude(pk=exclude_pk).exists()
        
        if not slug_exists and not article_exists:
            return base_slug, current_article
        
        current_article += 1
        attempts += 1
    
    raise ValidationError(f"Не удалось сгенерировать уникальный slug и article_number после {max_attempts} попыток.")

def get_unique_article_number(start_article_number):
    # Устарело: теперь интегрировано в generate_unique_slug (можно удалить, если не используется в другом коде)
    article_number = start_article_number
    while Product.objects.filter(article_number=article_number).exists():
        article_number += 1
    return article_number

def generate_unique_category_slug(name, exclude_pk=None):
    # Без изменений, но добавьте лимит, если нужно
    base_slug = slugify(unidecode(name))
    queryset = Category.objects.filter(slug=base_slug)
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    if queryset.exists():
        raise ValidationError("Такая категория уже существует.")
    return base_slug

# Определите CategorySerializer ПЕРВЫМ (перед ProductSerializer)
class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()  # Заменено на SerializerMethodField для рекурсии
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='parent', write_only=True, required=False
    )  # Для записи: передавать ID родителя

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'parent', 'parent_id']  # Добавлен parent_id
        read_only_fields = ['slug']

    def get_parent(self, obj):
        # Метод для SerializerMethodField: возвращает сериализованные данные родителя, если он есть
        if obj.parent:
            return CategorySerializer(obj.parent, context=self.context).data  # context для вложенных сериализаторов (например, для request)
        return None

    def validate(self, attrs):
        parent = attrs.get('parent')  # Получаем объект parent из attrs (после обработки source='parent')
        instance = getattr(self, 'instance', None)  # instance есть только в update
        
        if parent:
            if instance and parent == instance:
                raise serializers.ValidationError("Категория не может быть родителем самой себе.")
            # Опционально: проверка на цикл (рекурсивно проверяем ancestors)
            # Если parent имеет ancestors, и instance (или его descendants) в них — ошибка
            # Но для простоты: если дерево плоское, это достаточно. Для глубоких деревьев используйте django-mptt.
            current = parent
            while current.parent:
                if instance and current.parent == instance:
                    raise serializers.ValidationError("Установка этого parent создаст цикл в иерархии.")
                current = current.parent
        
        return attrs

    def create(self, validated_data):
        name = validated_data.get('name')
        if not name:
            raise serializers.ValidationError("Название категории обязательно.")
        
        # Генерируем slug и проверяем уникальность (exclude_pk=None для нового объекта)
        slug = generate_unique_category_slug(name)
        validated_data['slug'] = slug
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_name = validated_data.get('name', instance.name)
        
        # Генерируем новый slug только если name изменилось, и проверяем уникальность (исключая текущую категорию)
        if new_name != instance.name:
            new_slug = generate_unique_category_slug(new_name, exclude_pk=instance.pk)
            validated_data['slug'] = new_slug
        
        return super().update(instance, validated_data)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']
        extra_kwargs = {
            'product': {'read_only': True},  # Продукт устанавливается автоматически
        }

class ProductSerializer(serializers.ModelSerializer):
    sizes_and_prices = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=True
    )
    images = ProductImageSerializer(many=True, read_only=True)  # Сделано read_only — файлы обрабатываются вручную в views

    def get_sizes_and_prices(self, obj):
        product_prices = obj.product_prices.all()  # Используем related_name='product_prices' из модели ProductPrice
        return [
            {   'size_id': pp.size.id,  # ID размера (для ссылок)
                'size': pp.size.title,  # Название размера (строка)
                'price': pp.price,
                'old_price': pp.old_price if pp.old_price else None,
                'zacup_price': pp.zacup_price
            }
            for pp in product_prices
        ]

    def create(self, validated_data):
        title = validated_data.get('title')
        if not title:
            raise serializers.ValidationError("Название продукта обязательно.")
        
        article_number = validated_data.get('article_number')
        if article_number is None:
            article_number = generate_article_number()
        
        # Генерируем slug и корректируем article_number
        slug, corrected_article_number = generate_unique_slug(title, article_number)
        validated_data['slug'] = slug
        validated_data['article_number'] = corrected_article_number
        
        # Проверка уникальности article_number перед сохранением (защита от race condition)
        if Product.objects.filter(article_number=corrected_article_number).exists():
            raise serializers.ValidationError({"article_number": "Артикул уже занят."})
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_title = validated_data.get('title', instance.title)
        if not new_title:
            raise serializers.ValidationError("Название продукта обязательно.")
        
        article_number = instance.article_number  # Фиксирован
        
        # Генерируем slug с текущим article_number
        slug, _ = generate_unique_slug(new_title, article_number, exclude_pk=instance.pk)
        validated_data['slug'] = slug
        
        # Fallback: если всё ещё конфликт (редко), добавляем суффикс
        if Product.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            base_slug = slug
            counter = 1
            while Product.objects.filter(slug=f"{base_slug}-{counter}").exclude(pk=instance.pk).exists():
                counter += 1
            validated_data['slug'] = f"{base_slug}-{counter}"
        
        return super().update(instance, validated_data)
    
    # def get_description(self, obj):
    #     # Рендерим HTML из description, чтобы <br /> превращались в реальные переносы строк
    #     return mark_safe(obj.description) if obj.description else ''
    # get_description.short_description = 'Описание'


    class Meta:
        model = Product
        fields = [
            'category',
            'category_id',
            'id',
            'title',
            'description',
            'article_number',  # Может передаваться в create, генерируется автоматически если не передан
            'stock',
            'unit',
            'is_hidden',
            'mesto',
            'created',
            'updated',
            'slug',  # Генерируется автоматически
            'sizes_and_prices',
            'images'  # Теперь read_only
        ]
        extra_kwargs = {
            'slug': {'read_only': True},  # Не передаётся в input
            'article_number': {'required': False},  # Не обязательно в create (генерируется автоматически), игнорируется в update
        }
        read_only_fields = []  # Убрал article_number и slug отсюда для гибкости
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_price_id = serializers.IntegerField(write_only=True)  # Новое поле вместо product_id и size_id
        
    # Новое поле для изображений продукта
    product_images = serializers.SerializerMethodField()

    # Поле для места
    product_mesto = serializers.SerializerMethodField()
    
    # Добавлены поля для обработки snapshots: product_title, product_article и т.д. (а не через source)
    product_title = serializers.SerializerMethodField()
    product_article = serializers.SerializerMethodField()
    size_title = serializers.SerializerMethodField()
    zacup_price = serializers.SerializerMethodField()  # Добавлено для совместимости
    product_total_cost = serializers.SerializerMethodField()  # Добавлено для расчета стоимости
    
    # Новое поле для общего количества закупочного (для данного товара)
    product_total_zacup_price = serializers.SerializerMethodField()

    def get_product_title(self, obj):
        if obj.product_snapshot:
            return obj.product_snapshot
        elif obj.product_price and obj.product_price.product:
            return obj.product_price.product.title
        return "Товар удалён или в архиве"

    def get_product_article(self, obj):
        if obj.article_snapshot:
            return obj.article_snapshot
        elif obj.product_price and obj.product_price.product:
            return obj.product_price.product.article_number
        return "Артикул не указан"

    def get_product_mesto(self, obj):
        if obj.mesto_snapshot:
            return obj.mesto_snapshot
        elif obj.product_price and obj.product_price.product:
            return obj.product_price.product.mesto
        return "Место не указано"

    def get_size_title(self, obj):
        if obj.size_snapshot:
            return obj.size_snapshot
        elif obj.product_price and obj.product_price.size:
            return obj.product_price.size.title
        return "Размер отсутствует"

    def get_zacup_price(self, obj):
        # Обеспечиваем, что всегда возвращается число (float), а не None
        if obj.zacup_price_snapshot is not None:
            return int(obj.zacup_price_snapshot)  # Возвращаем как float для API (например, 650.0)
        elif obj.product_price and obj.product_price.zacup_price is not None:
            return int(obj.product_price.zacup_price)
        return 0.0  # Default к 0.0 если нет цены

    def get_product_total_cost(self, obj):
        return obj.get_cost()  # Предполагаю, что метод существует в модели

    def get_product_total_zacup_price(self, obj):
        """
        Calculated field: Total purchase quantity/cost for this item (zacup_price * quantity).
        Dynamically updates when quantity changes.
        """
        zacup_price = self.get_zacup_price(obj)  # Используем уже обработанную закупочную цену (число)
        return float(zacup_price * obj.quantity)

    def get_product_images(self, obj):
        if not obj.product_price:
            return []  # Если product_price удалён, возвращаем пустой список
        try:
            request = self.context.get('request')
            images = []
            for img in obj.product_price.product.images.all():
                if img.image:
                    if request:
                        full_url = request.build_absolute_uri(img.image.url)
                    else:
                        full_url = img.image.url
                    images.append(full_url)
            return images
        except (Product.DoesNotExist, AttributeError):
            return []

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_price_id', 'product_title', 'product_article', 'size_title',
            'price', 'quantity','zacup_price', 'product_mesto', 'product_images',
            'product_total_cost', 'product_total_zacup_price',
            # склад
            'picked_quantity',
            'picked_zacup_price',
            'picked_comment',
            'is_picked',  
        ]
        read_only_fields = [
            'id', 'product_title', 'product_article', 'size_title', 'zacup_price',
            'product_mesto', 'product_images', 'product_total_cost', 'product_total_zacup_price'
        ]

    def validate(self, data):
        product_price_id = data.get('product_price_id')
        if product_price_id:
            try:
                product_price = ProductPrice.objects.get(id=product_price_id)
                if getattr(product_price, 'hidden', False):  # Пример: если есть поле hidden
                    raise serializers.ValidationError("Этот товар недоступен для заказа.")
                # Другие проверки: availability, stock и т.д.
            except ProductPrice.DoesNotExist:
                raise serializers.ValidationError("Цена для данного товара и размера не найдена.")
        return data 

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False, read_only=True)  # Вложенные items для чтения/обновления
    delivery_method_title = serializers.CharField(source='delivery_method.title', read_only=True)
    discount_title = serializers.SerializerMethodField()  # Убрали дублирование (было CharField); оставили как метод для гибкости
    status = serializers.SerializerMethodField()
    get_total_zakup_cost = serializers.SerializerMethodField()  # Добавлено для расчета общей закупной стоимости

    # read‑only поля для отображения посредника
    assigned_to_id = serializers.IntegerField(source='assigned_to.id', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_to_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'first_name_last_name', 'email', 'phone', 'region', 'city', 'address', 'postal_code',
            'passport_number', 'comment', 'my_comment', 'created', 'updated', 'paid', 'zamena_product',
            'strahovat_gruz', 'soglasie_na_obrabotku_danyh', 'soglasie_na_uslovie_sotrudnichestva',
            'status', 'delivery_method_title', 'price_delivery', 'discount_title',
            'items', 'get_total_cost', 'get_total_zakup_cost','assigned_to_id',
            'assigned_to_username',
            'assigned_to_full_name',
        ]
        read_only_fields = ['id', 'created', 'updated', 'get_total_cost', 'get_total_zakup_cost']  # Добавлено в read_only, так как вычисляется динамически


    def get_assigned_to_full_name(self, obj):
        """
        Собираем красивое ФИО посредника.
        Если first_name/last_name пустые — возвращаем username.
        Если assigned_to = None — возвращаем None.
        """
        if not obj.assigned_to:
            return None
        full = f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return full or obj.assigned_to.username
    
    
    
    def get_discount_title(self, obj):
        if obj.discount:
            if obj.discount.discount_type == 'amount':
                return f'Скидка в рублях: {obj.discount.discount_value}'
            elif obj.discount.discount_type == 'percentage':
                return f'Скидка в %: {obj.discount.discount_value}'
            else:
                return f'Неизвестный тип скидки: {obj.discount.discount_value}'
        return None  # Или пустую строку

    def get_get_total_zakup_cost(self, obj):  # Метод для расчета общей закупной стоимости заказа
        total_zakup = sum(
            ((item.zacup_price_snapshot if item.zacup_price_snapshot is not None 
              else (item.product_price.zacup_price if item.product_price and item.product_price.zacup_price is not None else 0)) 
             * item.quantity)
            for item in obj.items.all()
        )
        return total_zakup

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Обновляем поля Order
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем items: Полностью заменяем (как в примере с images)
        if items_data is not None:
            instance.items.all().delete()  # Удаляем старые
            for item_data in items_data:
                product_price_id = item_data.get('product_price_id')
                if not product_price_id:
                    raise serializers.ValidationError("Не указан product_price_id для item.")
                try:
                    product_price = ProductPrice.objects.get(id=product_price_id)  # Строго проверяем существование перед create
                except ProductPrice.DoesNotExist:
                    raise serializers.ValidationError(f"ProductPrice с id {product_price_id} не найден.")
                OrderItem.objects.create(order=instance, product_price=product_price, price=item_data.get('price'), quantity=item_data.get('quantity'))  # Изменено: используем product_price вместо product_id/size_id
        
        return instance

    def validate(self, data):
        # Дополнительная валидация: Проверяем, что статус корректный
        status = data.get('status')
        if status and status not in dict(Order.STATUS_CHOICES):
            raise serializers.ValidationError({"status": "Некорректный статус."})
        return data

    def get_status(self, obj):
        return obj.get_status_display()
    



class OrderItemPickingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'picked_quantity',
            'picked_zacup_price',
            'picked_comment',
            'is_picked',
        ] 
