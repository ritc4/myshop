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
        return reverse("home:product_list_by_category", kwargs={"slug": self.slug})
    
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
    title = models.CharField(max_length=10, unique=True,verbose_name="Размеры")  # Название размера

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'


class Product(models.Model):
    title = models.CharField(max_length=255,verbose_name='Название товара')
    description = models.TextField(max_length=255,blank=True,verbose_name='Описание')
    article_number = models.IntegerField(unique=True,verbose_name='Артикул')
    price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена продажи')
    zacup_price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена закупки')
    old_price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена старая')
    stock = models.IntegerField(default=100, validators=[MinValueValidator(0)],verbose_name='Остаток')  # Остаток товара в штуках
    unit = models.CharField(max_length=10, default='шт',verbose_name='Единица измерения')  # Единица измерения, по умолчанию 'шт'
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True,verbose_name='Фото')  # Поле для изображения
    is_hidden = models.BooleanField(default=False,verbose_name='Скрыть товар')  # Поле для скрытия товара
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)  # Поле slug
    size = models.ManyToManyField(Size, blank=True,related_name='size',verbose_name='Размер') # Связь с моделью Size
    category = TreeForeignKey(Category, on_delete=models.PROTECT,related_name='cat',verbose_name='Категория')  

    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['title']),
            models.Index(fields=['-created']),
        ]
    
    
    
    def __str__(self):
        return f"{self.title} ({self.stock} {self.unit}, Размеры: {self.size})"
    
    def get_absolute_url(self):
        return reverse("home:product_detail", kwargs={"slug": self.slug, "id":self.id})
    

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'