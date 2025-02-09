from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django.core.validators import MinValueValidator

class Category(MPTTModel):
    name = models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField(max_length=255,verbose_name='Url',unique=True)

    def get_absolute_url(self):
        return reverse("home:category", kwargs={"slug": self.slug})
    
    def __str__(self):
        return self.name
    

    class MPTTMeta:
        order_insertion_by = ['name']


class Size(models.Model):
    title = models.CharField(max_length=10, unique=True)  # Название размера

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255,blank=True)
    article_number = models.IntegerField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    zacup_price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=100, validators=[MinValueValidator(0)])  # Остаток товара в штуках
    unit = models.CharField(max_length=10, default='шт')  # Единица измерения, по умолчанию 'шт'
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Поле для изображения
    is_hidden = models.BooleanField(default=False,verbose_name='Скрыть товар')  # Поле для скрытия товара
    slug = models.SlugField(max_length=200, unique=True)  # Поле slug
    size = models.ForeignKey(Size, on_delete=models.CASCADE,related_name='siz') # Связь с моделью Size
    category = TreeForeignKey(Category, on_delete=models.PROTECT,related_name='cat')  

    def __str__(self):
        return f"{self.title} ({self.stock} {self.unit}, Размер: {self.size})"
    
    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})
    