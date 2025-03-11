from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django.core.validators import MinValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings




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

    def get_breadcrumbs(self):
        return self.get_ancestors(include_self=True)
        


class Size(models.Model):
    title = models.CharField(max_length=50, unique=True,verbose_name="Размеры")  # Название размера

    def __str__(self):
        return f"{self.title}"
    
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
        indexes = [
            models.Index(fields=['product']),  # Индекс для поля product
        ]
    

class Product(models.Model):
    title = models.CharField(max_length=255,verbose_name='Название товара')
    description = CKEditor5Field(config_name='extends',max_length=255,blank=True,verbose_name='Описание')
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
            models.Index(fields=['category']),  # Индекс для поля category
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


class News(models.Model):
    title = models.CharField(max_length=255,verbose_name='Новость',blank=False)
    description = CKEditor5Field(config_name='extends',verbose_name='Описание новости',blank=False)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.title}"
    

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class SizeTable(models.Model):
    title = models.CharField(max_length=255,verbose_name='Размерная таблица',blank=False)
    image = models.ImageField(upload_to='size_table/%Y/%m/%d', blank=True,null=True, verbose_name='Изображение')


    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = 'Размерная таблица'
        verbose_name_plural = 'Размерные таблицы'


class Uslovie_firm(models.Model):
    title = models.CharField(max_length=255,verbose_name='Условие сотрудничества',blank=False)
    description = CKEditor5Field(config_name='extends',verbose_name='Описание',blank=False)


    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = 'Условие сотрудничества'
        verbose_name_plural = 'Условия сотрудничества'


class Politica_firm(models.Model):
    title = models.CharField(max_length=255,verbose_name='Политика конфиденциальности',blank=False)
    description = CKEditor5Field(config_name='extends',verbose_name='Описание',blank=False)

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = 'Политика конфиденциальности'
        verbose_name_plural = 'Политика конфиденциальности'

class ImageSliderHome(models.Model):
    image = models.ImageField(upload_to='slider_home/%Y/%m/%d', blank=True,null=True, verbose_name='Изображение')


    class Meta:
        verbose_name = 'Изображение главной страницы'
        verbose_name_plural = 'Изображения главной страницы'


class DeliveryInfo(models.Model):
    title = models.CharField(max_length=255,verbose_name='Доставка',blank=False)
    description = CKEditor5Field(config_name='extends',verbose_name='Описание',blank=False)

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = 'Информацию по доставке'
        verbose_name_plural = 'Информация по доставке'




class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Связь с пользователем
    content = models.TextField(verbose_name="Отзыв", blank=False)
    kachestvo_rating = models.PositiveIntegerField(default=0,blank=False,verbose_name='Качество товара')  # Рейтинг за качество
    obsluga_rating = models.PositiveIntegerField(default=0,blank=False,verbose_name='Качество обслуживания')    # Рейтинг за обслуживание
    sroki_rating = models.PositiveIntegerField(default=0,blank=False,verbose_name='Соблюдение сроков')  # Рейтинг за сроки
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return str(self.user) if self.user else "Анонимный пользователь"  # Возвращаем строку


    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='review_home/%Y/%m/%d', blank=True, null=True, verbose_name='Изображение')

    
    def __str__(self):
        return f"{self.review}"
    
    def image_tag_review(self):
        # Возвращаем все изображения, связанные с продуктом
        return self.review.image.all()
    image_tag_review.short_description = "Изображение"
    
    class Meta:
        verbose_name = 'Изображение отзыва'
        verbose_name_plural = 'Изображения отзывов'