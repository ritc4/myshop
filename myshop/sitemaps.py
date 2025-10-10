# myshop/sitemaps.py
from django.contrib.sitemaps import Sitemap

# Импорты из ваших моделей (из home/models.py)
from home.models import Category, Product

# Sitemap для категорий (из Category)
class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Category.objects.all()
    
    def lastmod(self, obj):
        # В модели Category нет поля created/updated; используйте None
        # Если хотите, добавьте поле updated_at в модель Category
        return None
    
    def location(self, obj):
        return obj.get_absolute_url()  # Использует reverse('home:category', kwargs={'slug': obj.slug})

# Sitemap для товаров (из Product)
class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    
    def items(self):
        return Product.objects.filter(is_hidden=False)
    
    def lastmod(self, obj):
        return obj.updated  # Поле updated есть в модели Product
    
    def location(self, obj):
        return obj.get_absolute_url()  # Использует reverse('home:product_detail', kwargs={'id': obj.id, 'slug': obj.slug})

# Словарь sitemaps (только categories и products)
sitemaps = {
    'categories': CategorySitemap,
    'products': ProductSitemap,
}
