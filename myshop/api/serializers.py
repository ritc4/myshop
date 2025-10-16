# from rest_framework import serializers
# from ..models import Product,Category

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'slug']

# class ProductSerializer(serializers.ModelSerializer):
#     # Кастомное поле для размеров и цен
#     sizes_and_prices = serializers.SerializerMethodField()
    
#     # Вложенная сериализация категории
#     category = CategorySerializer(read_only=True)  # Вместо простого ID — объект категории


#     def get_sizes_and_prices(self, obj):
#         product_prices = obj.product_prices.all()
#         return [
#             {
#                 'size': pp.size.title,
#                 'price': pp.price,
#                 'old_price': pp.old_price if pp.old_price else None
#             }
#             for pp in product_prices
#         ]

#     class Meta:
#         model = Product
#         fields = '__all__'  # Теперь category будет вложенным объектом





from rest_framework import serializers
from home.models import Product, Category, ProductImage  # Добавлен ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Добавлено для изображения категории

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'image']

class ProductSerializer(serializers.ModelSerializer):
    # Кастомное поле для размеров и цен (read-only)
    sizes_and_prices = serializers.SerializerMethodField()
    
    # Вложенная сериализация категории
    category = CategorySerializer(read_only=True)  # Вместо простого ID — объект категории
    
    # Nested для изображений (required=False для создания без изображений)
    images = ProductImageSerializer(many=True, required=False)

    def get_sizes_and_prices(self, obj):
        product_prices = obj.product_prices.all()
        return [
            {
                'size': pp.size.title,
                'price': pp.price,
                'old_price': pp.old_price if pp.old_price else None
            }
            for pp in product_prices
        ]

    def create(self, validated_data):
        # Извлекаем nested изображения
        images_data = validated_data.pop('images', [])
        # Создаём продукт (без изображений)
        product = Product.objects.create(**validated_data)
        # Создаём связанные изображения
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        return product

    def update(self, instance, validated_data):
        # Извлекаем nested изображения
        images_data = validated_data.pop('images', [])
        # Обновляем основные поля продукта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Удаляем старые изображения и создаём новые (простая замена; можно улучшить для частичного обновления)
        instance.images.all().delete()
        for image_data in images_data:
            ProductImage.objects.create(product=instance, **image_data)
        return instance

    class Meta:
        model = Product
        fields = '__all__'  # Включает все поля Product + кастомные (category, sizes_and_prices, images)
