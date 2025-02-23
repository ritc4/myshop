from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django.core.validators import MinValueValidator



class Category(MPTTModel):
    name = models.CharField(max_length=255, unique=True,verbose_name='Категория')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',verbose_name='Подкатегория')
    slug = models.SlugField(max_length=255,verbose_name='Url',unique=True)
    image = models.ImageField(upload_to='categories/%Y/%m/%d', blank=True, null=True,verbose_name='Фото')  # Поле для изображения категории

    def get_absolute_url(self):
        return reverse("home:category", kwargs={"slug": self.slug})
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'
        indexes = [
            models.Index(fields=['name']),]

    class MPTTMeta:
        order_insertion_by = ['name']
        


class Size(models.Model):
    title = models.CharField(max_length=50, unique=True,verbose_name="Размеры")  # Название размера

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'



class ProductPrice(models.Model):
    product = models.ForeignKey('Product', related_name='product_prices', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='product_size', on_delete=models.CASCADE,verbose_name='Размер')
    price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена продажи')
    old_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Цена старая ', null=True, blank=True)
    zacup_price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена закупки')
    
    def __str__(self):
        return f"{self.product.title}"
    
    class Meta:
        verbose_name = 'Размер и Цена товара'
        verbose_name_plural = 'Размеры и Цены товара'
    

class Product(models.Model):
    title = models.CharField(max_length=255,verbose_name='Название товара')
    description = models.TextField(max_length=255,blank=True,verbose_name='Описание')
    article_number = models.IntegerField(unique=True,verbose_name='Артикул')
    stock = models.IntegerField(default=100, validators=[MinValueValidator(0)],verbose_name='Остаток')  # Остаток товара в штуках
    unit = models.CharField(max_length=10, default='шт',verbose_name='Единица измерения')  # Единица измерения, по умолчанию 'шт'
    is_hidden = models.BooleanField(default=False,verbose_name='Скрыть товар')  # Поле для скрытия товара
    mesto = models.CharField(max_length=20,blank=True,null=True,verbose_name='Место')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)  # Поле slug
    category = TreeForeignKey(Category, on_delete=models.PROTECT,related_name='cat',verbose_name='Категория')  
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['title']),
            models.Index(fields=['-created']),
        ]
    
    
    def __str__(self):
        return f"{self.title}"
    
    def get_absolute_url(self):
        return reverse("home:product_detail", kwargs={"slug": self.slug, "id":self.id})
    

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True, verbose_name='Изображение')
    
    def __str__(self):
        return f"Изображение {self.id}"
    

    def image_tag(self):
        # Возвращаем все изображения, связанные с продуктом
        return self.product.image.all()
    image_tag.short_description = "Фото"
    
    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'