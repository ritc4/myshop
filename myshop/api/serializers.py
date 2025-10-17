# from unidecode import unidecode
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError  # Добавлено
# from home.models import Category, Product, ProductImage, Size, ProductPrice  # Обновите импорты на основе ваших моделей
# from django.utils.text import slugify

# def generate_article_number():
#     last_product = Product.objects.order_by('-article_number').first()
#     if last_product:
#         return last_product.article_number + 1
#     return 1

# def generate_unique_slug(title, article_number, exclude_pk=None):
#     """
#     Генерирует уникальный slug и article_number.
#     Формат slug: slugified(title)-article_number.
#     Если конфликт (slug или article_number), увеличивает article_number до уникальности.
#     Возвращает (slug, corrected_article_number).
#     """
#     if not title or article_number is None:
#         raise ValidationError("Название и артикул обязательны для генерации slug.")
    
#     current_article = article_number
#     max_attempts = 10000  # Лимит для избежания бесконечного цикла
#     attempts = 0
    
#     while attempts < max_attempts:
#         base_slug = slugify(f"{unidecode(title)}-{current_article}")
#         # Проверяем уникальность slug И article_number (исключая exclude_pk)
#         slug_exists = Product.objects.filter(slug=base_slug).exclude(pk=exclude_pk).exists()
#         article_exists = Product.objects.filter(article_number=current_article).exclude(pk=exclude_pk).exists()
        
#         if not slug_exists and not article_exists:
#             return base_slug, current_article
        
#         current_article += 1
#         attempts += 1
    
#     raise ValidationError(f"Не удалось сгенерировать уникальный slug и article_number после {max_attempts} попыток.")

# def get_unique_article_number(start_article_number):
#     # Устарело: теперь интегрировано в generate_unique_slug
#     article_number = start_article_number
#     while Product.objects.filter(article_number=article_number).exists():
#         article_number += 1
#     return article_number

# def generate_unique_category_slug(name, exclude_pk=None):
#     # Без изменений, но добавьте лимит, если нужно
#     base_slug = slugify(unidecode(name))
#     queryset = Category.objects.filter(slug=base_slug)
#     if exclude_pk:
#         queryset = queryset.exclude(pk=exclude_pk)
#     if queryset.exists():
#         raise ValidationError("Такая категория уже существует.")
#     return base_slug

# # Определите CategorySerializer ПЕРВЫМ (перед ProductSerializer)
# class CategorySerializer(serializers.ModelSerializer):
#     parent = serializers.SerializerMethodField()  # Заменено на SerializerMethodField для рекурсии
#     parent_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(), source='parent', write_only=True, required=False
#     )  # Для записи: передавать ID родителя

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'slug', 'image', 'parent', 'parent_id']  # Добавлен parent_id
#         read_only_fields = ['slug']

#     def get_parent(self, obj):
#         # Метод для SerializerMethodField: возвращает сериализованные данные родителя, если он есть
#         if obj.parent:
#             return CategorySerializer(obj.parent, context=self.context).data  # context для вложенных сериализаторов (например, для request)
#         return None

#     def validate(self, attrs):
#         parent = attrs.get('parent')  # Получаем объект parent из attrs (после обработки source='parent')
#         instance = getattr(self, 'instance', None)  # instance есть только в update
        
#         if parent:
#             if instance and parent == instance:
#                 raise serializers.ValidationError("Категория не может быть родителем самой себе.")
#             # Опционально: проверка на цикл (рекурсивно проверяем ancestors)
#             # Если parent имеет ancestors, и instance (или его descendants) в них — ошибка
#             # Но для простоты: если дерево плоское, это достаточно. Для глубоких деревьев используйте django-mptt.
#             current = parent
#             while current.parent:
#                 if instance and current.parent == instance:
#                     raise serializers.ValidationError("Установка этого parent создаст цикл в иерархии.")
#                 current = current.parent
        
#         return attrs

#     def create(self, validated_data):
#         name = validated_data.get('name')
#         if not name:
#             raise serializers.ValidationError("Название категории обязательно.")
        
#         # Генерируем slug и проверяем уникальность (exclude_pk=None для нового объекта)
#         slug = generate_unique_category_slug(name)
#         validated_data['slug'] = slug
        
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         new_name = validated_data.get('name', instance.name)
        
#         # Генерируем новый slug только если name изменилось, и проверяем уникальность (исключая текущую категорию)
#         if new_name != instance.name:
#             new_slug = generate_unique_category_slug(new_name, exclude_pk=instance.pk)
#             validated_data['slug'] = new_slug
        
#         return super().update(instance, validated_data)



# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = ['image']
#         extra_kwargs = {
#             'product': {'read_only': True},  # Продукт устанавливается автоматически
#         }

# class ProductSerializer(serializers.ModelSerializer):
#     sizes_and_prices = serializers.SerializerMethodField()
#     category = CategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(), source='category', write_only=True, required=True
#     )
#     images = ProductImageSerializer(many=True, read_only=True)  # Сделано read_only — файлы обрабатываются вручную в views

#     def get_sizes_and_prices(self, obj):
#         product_prices = obj.product_prices.all()  # Используем related_name='product_prices' из модели ProductPrice
#         return [
#             {   'size_id': pp.size.id,  # ID размера (для ссылок)
#                 'size': pp.size.title,  # Название размера (строка)
#                 'price': pp.price,
#                 'old_price': pp.old_price if pp.old_price else None,
#                 'zacup_price': pp.zacup_price
#             }
#             for pp in product_prices
#         ]

#     def create(self, validated_data):
#         title = validated_data.get('title')
#         if not title:
#             raise serializers.ValidationError("Название продукта обязательно.")
        
#         if 'article_number' not in validated_data or validated_data.get('article_number') is None:
#             article_number = generate_article_number()
#             validated_data['article_number'] = article_number
#         else:
#             start_article_number = validated_data['article_number']
#             article_number = get_unique_article_number(start_article_number)
#             validated_data['article_number'] = article_number
        
#         # Генерируем уникальный slug (exclude_pk=None для create — всегда уникален)
#         slug = generate_unique_slug(title, article_number)
#         validated_data['slug'] = slug
        
#         instance = Product.objects.create(**validated_data)
#         return instance

#     def update(self, instance, validated_data):
#         new_title = validated_data.get('title', instance.title)
#         article_number = instance.article_number
        
#         # Генерируем новый slug, исключая текущий продукт из проверки
#         new_slug = generate_unique_slug(new_title, article_number, exclude_pk=instance.pk)
        
#         # Обновляем только если slug изменился (оптимизация)
#         if new_slug != instance.slug:
#             validated_data['slug'] = new_slug
        
#         validated_data.pop('article_number', None)
#         instance = super().update(instance, validated_data)
#         return instance

#     class Meta:
#         model = Product
#         fields = [
#             'category',
#             'category_id',
#             'id',
#             'title',
#             'description',
#             'article_number',  # Может передаваться в create, генерируется автоматически если не передан
#             'stock',
#             'unit',
#             'is_hidden',
#             'mesto',
#             'created',
#             'updated',
#             'slug',  # Генерируется автоматически
#             'sizes_and_prices',
#             'images'  # Теперь read_only
#         ]
#         extra_kwargs = {
#             'slug': {'read_only': True},  # Не передаётся в input
#             'article_number': {'required': False},  # Не обязательно в create (генерируется автоматически), игнорируется в update
#         }
#         read_only_fields = []  # Убрал article_number и slug отсюда для гибкости






from unidecode import unidecode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError  # Добавлено
from home.models import Category, Product, ProductImage, Size, ProductPrice  # Обновите импорты на основе ваших моделей
from orders.models import Order, OrderItem, DeliveryMethod, Discount
from django.utils.text import slugify

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
    # Устарело: теперь интегрировано в generate_unique_slug
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
    product_title = serializers.CharField(source='product.title', read_only=True)
    size_title = serializers.CharField(source='size.title', read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    size_id = serializers.IntegerField(write_only=True)
    
    
    # Новое поле для изображений продукта
    product_images = serializers.SerializerMethodField()
    
    # Поле для закупочной цены (метод модели)
    product_zacup_price = serializers.SerializerMethodField()

    # Поле для закупочной цены (метод модели)
    product_mesto = serializers.SerializerMethodField()

    def get_product_images(self, obj):
        # Получаем request из контекста
        request = self.context.get('request')
        images = []
        for img in obj.product.images.all():
            if img.image:
                # Если request доступен, строим абсолютный URL
                if request:
                    full_url = request.build_absolute_uri(img.image.url)
                else:
                    # Фallback на относительный URL (для тестов или других случаев)
                    full_url = img.image.url
                images.append(full_url)
        return images  # Возвращаем список абсолютных URL

    def get_product_zacup_price(self, obj):
        # Возвращаем закупочную цену для текущего размера (из метода модели)
        return obj.product_zacup_price()
    
    def get_product_mesto(self, obj):
        return obj.product.mesto

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'size_id', 'product_title', 'size_title','price', 'quantity', 'product_zacup_price', 'product_mesto', 'product_images']
        read_only_fields = ['id', 'product_title', 'size_title', 'product_zacup_price','product_mesto', 'product_images']

    def validate(self, data):
        product_id = data.get('product_id')
        size_id = data.get('size_id')
        try:
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(id=size_id)
            # Проверяем, есть ли цена для этого размера
            if not product.product_prices.filter(size=size).exists():
                raise serializers.ValidationError("Цена для данного размера не найдена.")
        except (Product.DoesNotExist, Size.DoesNotExist):
            raise serializers.ValidationError("Продукт или размер не найден.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)  # Вложенные items для чтения/обновления
    delivery_method_title = serializers.CharField(source='delivery_method.title', read_only=True)
    discount_title = serializers.CharField(source='discount.__str__', read_only=True)

    discount_title = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'first_name_last_name', 'email', 'phone', 'region', 'city', 'address', 'postal_code',
            'passport_number', 'comment', 'my_comment', 'created', 'updated', 'paid', 'zamena_product',
            'strahovat_gruz', 'soglasie_na_obrabotku_danyh', 'soglasie_na_uslovie_sotrudnichestva',
            'status', 'delivery_method', 'delivery_method_title', 'price_delivery', 'discount', 'discount_title',
            'items', 'get_total_cost'  # Добавлено для чтения общей стоимости
        ]
        read_only_fields = ['id', 'created', 'updated', 'get_total_cost']

    def get_discount_title(self, obj):
        if obj.discount:  # Проверяем, есть ли скидка
            return obj.discount.title  # Возвращаем title скидки
        return None  

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
                OrderItem.objects.create(order=instance, **item_data)
        
        return instance

    def validate(self, data):
        # Дополнительная валидация: Проверяем, что статус корректный
        status = data.get('status')
        if status and status not in dict(Order.STATUS_CHOICES):
            raise serializers.ValidationError({"status": "Некорректный статус."})
        return data











