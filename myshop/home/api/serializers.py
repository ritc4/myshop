from rest_framework import serializers
from ..models import Product,Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    # Кастомное поле для размеров и цен
    sizes_and_prices = serializers.SerializerMethodField()
    
    # Вложенная сериализация категории
    category = CategorySerializer(read_only=True)  # Вместо простого ID — объект категории


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

    class Meta:
        model = Product
        fields = '__all__'  # Теперь category будет вложенным объектом
