from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.utils.html import format_html
from datetime import datetime
from django.utils import timezone
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
import io
import os
from django.utils.text import slugify





def validate_file_size(value):  
    max_size = 20 * 1024 * 1024  # 20 MB  
    if value.size > max_size:  
        raise ValidationError(f'File size must be under {max_size} bytes.') 


def validate_image_mime_type(value):
    """
    Валидатор для проверки MIME-типа изображения через Pillow.
    Разрешает только реальные изображения (JPEG, PNG, GIF, WebP).
    """
    allowed_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    
    try:
        # Открываем файл как байты и проверяем через Pillow
        image = Image.open(io.BytesIO(value.read()))
        mime_type = Image.MIME.get(image.format)  # Получаем MIME-тип по формату (e.g., 'JPEG' -> 'image/jpeg')
        
        if mime_type not in allowed_mime_types:
            raise ValidationError(f'Недопустимый тип файла: {mime_type}. Разрешены только изображения.')
        
        # Сбрасываем указатель файла для дальнейшей обработки
        value.seek(0)
    except Exception as e:
        raise ValidationError(f'Ошибка при проверке изображения: {str(e)}')




# class Category(MPTTModel):
#     name = models.CharField(max_length=255, unique=True,verbose_name='Категория')
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',verbose_name='Подкатегория')
#     slug = models.SlugField(max_length=255,verbose_name='Url',unique=True)
#     image = models.ImageField(upload_to='categories/%Y/%m/%d', blank=True, null=True,verbose_name='Фото')  # Поле для изображения категории

#     def get_absolute_url(self):
#         return reverse("home:category", kwargs={"slug": self.slug})
    
#     def __str__(self):
#         return self.name
    
#     class Meta:
#         verbose_name = 'Категорию'
#         verbose_name_plural = 'Категории'
#         indexes = [
#             models.Index(fields=['name']),]

#     class MPTTMeta:
#         order_insertion_by = ['name']

#     def get_breadcrumbs(self):
#         return self.get_ancestors(include_self=True)


# Функция для пути категорий (уже была, теперь используется)
def category_image_upload_path(instance, filename):
    category_slug = slugify(instance.name)
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    path = f'categories/{category_slug}/{year}/{month}/{day}/'
    return os.path.join(path, filename)




class Category(MPTTModel):
    name = models.CharField(max_length=255, unique=True,verbose_name='Категория')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',verbose_name='Подкатегория')
    slug = models.SlugField(max_length=255,verbose_name='Url',unique=True)
    image = ProcessedImageField(
        upload_to=category_image_upload_path,
        processors=[ResizeToFit(400, 400, upscale=False)],  # Пример размера для миниатюр категорий
        format='WEBP',
        options={'quality': 95, 'optimize': True},
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size,  # Меньше, если не нужно
            validate_image_mime_type,  # Новый валидатор
        ],
        blank=True,
        null=True, 
        verbose_name='Фото',
    )


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
    title = models.CharField(max_length=50, unique=True,verbose_name="Размеры",db_index=True)  # Название размера

    def __str__(self):
        return f"{self.title}"
     
    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры' 



class ProductPrice(models.Model):
    product = models.ForeignKey('Product', related_name='product_prices', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='product_size', on_delete=models.CASCADE,verbose_name='Размер')
    price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена продажи',db_index=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Цена старая ', null=True, blank=True,db_index=True)
    zacup_price = models.DecimalField(max_digits=10, decimal_places=0,verbose_name='Цена закупки',db_index=True)
    
    def __str__(self):
        return f"{self.product.title}"
    
    class Meta:
        verbose_name = 'Размер и Цена товара'
        verbose_name_plural = 'Размеры и Цены товара'
        indexes = [
            models.Index(fields=['product']),  # Индекс для поля product
            models.Index(fields=['size']),  # Индекс для поля size
        ]
    

class Product(models.Model):
    title = models.CharField(max_length=255,verbose_name='Название товара')
    description = CKEditor5Field(config_name='extends',max_length=255,blank=True,verbose_name='Описание',db_index=True)
    article_number = models.IntegerField(unique=True,verbose_name='Артикул',db_index=True)
    stock = models.IntegerField(default=100, validators=[MinValueValidator(0)],verbose_name='Остаток',db_index=True)  # Остаток товара в штуках
    unit = models.CharField(max_length=10, default='шт',verbose_name='Единица измерения',db_index=True)  # Единица измерения, по умолчанию 'шт'
    is_hidden = models.BooleanField(default=False,verbose_name='Скрыть товар',db_index=True)  # Поле для скрытия товара
    mesto = models.CharField(max_length=20,blank=True,null=True,verbose_name='Место',db_index=True)
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
            models.Index(fields=['category']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
    
    
    def __str__(self):
        return f"{self.title}"
    
    def get_absolute_url(self):
        return reverse("home:product_detail", kwargs={"slug": self.slug, "id":self.id})


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    



def product_image_upload_path(instance, filename):
    # Путь: products/%Y/%m/%d/{category_slug}/filename
    now = datetime.now()
    year, month, day = now.year, f"{now.month:02d}", f"{now.day:02d}"
    category_slug = instance.product.category.slug if instance.product.category else "no-category"  # Защита от пустого slug
    return f"products/{year}/{month}/{day}/{category_slug}/{filename}"



# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to=product_image_upload_path,blank=True,null=True, verbose_name='Изображение',db_index=True)
    
#     def __str__(self):
#         return f"Изображение {self.id} для {self.product.title}"
    
#     def image_tag(self):
#         if self.image:
#             return format_html('<img src="{}" width="100" height="100" />', self.image.url)
#         return "Нет изображения"
#     image_tag.short_description = "Фото"
    
#     class Meta:
#         verbose_name = 'Фото товара'
#         verbose_name_plural = 'Фото товаров'



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = ProcessedImageField(
        upload_to=product_image_upload_path,  # Без расширения, для перезаписи
        processors=[ResizeToFit(1000, 800, upscale=False)],  # Подгонка под 800x600
        format='WEBP',
        options={'quality': 95, 'optimize': True},
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size,  # 20 MB
            validate_image_mime_type,  # Новый валидатор
        ],
        blank=True,
        null=True, verbose_name='Изображение', db_index=True,
    )

    def __str__(self):
        return f"Изображение {self.id} для {self.product.title}"
    
    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" width="100" height="100" />', self.image.url)
        return "Нет изображения"
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


# class SizeTable(models.Model):
#     title = models.CharField(max_length=255,verbose_name='Размерная таблица',blank=False)
#     image = models.ImageField(upload_to='size_table/%Y/%m/%d', blank=True,null=True, verbose_name='Изображение')


#     def __str__(self):
#         return f"{self.title}"
    
#     class Meta:
#         verbose_name = 'Размерная таблица'
#         verbose_name_plural = 'Размерные таблицы'




class SizeTable(models.Model):
    title = models.CharField(max_length=255,verbose_name='Размерная таблица', blank=False)
    image = ProcessedImageField(
        upload_to='size_table/%Y/%m/%d',
        processors=[ResizeToFit(800, 600, upscale=False)],
        format='WEBP',
        options={'quality': 95, 'optimize': True},
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size,
            validate_image_mime_type,  # Новый валидатор
        ],
        blank=True,
        null=True, verbose_name='Изображение',
    )

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

# class ImageSliderHome(models.Model):
#     image = models.ImageField(upload_to='slider_home/%Y/%m/%d', blank=True,null=True, verbose_name='Изображение')


#     def __str__(self):
#         return f"{self.image}"


#     class Meta:
#         verbose_name = 'Изображение главной страницы'
#         verbose_name_plural = 'Изображения главной страницы'




class ImageSliderHome(models.Model):
    image = ProcessedImageField(
        upload_to='slider_home/%Y/%m/%d',
        processors=[ResizeToFit(1600, 800, upscale=False)],
        format='WEBP',
        options={'quality': 100, 'optimize': True},
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size,
            validate_image_mime_type,  # Новый валидатор
        ],
        blank=True,
        null=True, verbose_name='Изображение',
    )
    
    def __str__(self):
        return f"{self.image}"


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,db_index=True)  # Связь с пользователем
    content = models.TextField(verbose_name="Отзыв", blank=False)
    kachestvo_rating = models.PositiveIntegerField(default=0,blank=False,verbose_name='Качество товара',db_index=True)  # Рейтинг за качество
    obsluga_rating = models.PositiveIntegerField(default=0,blank=False,verbose_name='Качество обслуживания',db_index=True)    # Рейтинг за обслуживание
    sroki_rating = models.PositiveIntegerField(default=0,blank=False,verbose_name='Соблюдение сроков',db_index=True)  # Рейтинг за сроки
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)  

    def __str__(self):
        return str(self.user) if self.user else "Анонимный пользователь"  # Возвращаем строку


    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


# Функция для динамического пути загрузки изображений
def review_image_upload_path(instance, filename):
    # Получаем логин пользователя из связанного отзыва
    user_login = instance.review.user.username if instance.review.user else 'anonymous'
    # Получаем дату из отзыва (год/месяц/день)
    if instance.review.created_at:
        date_str = instance.review.created_at.strftime('%Y/%m/%d')
    else:
        date_str = 'unknown'
    # Возвращаем путь: review_home/username/год/месяц/день/filename
    return f'review_home/{user_login}/{date_str}/{filename}'


# class ReviewImage(models.Model):
#     review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to=review_image_upload_path, blank=True, null=True, verbose_name='Изображение',db_index=True)

    
#     def __str__(self):
#         return f"{self.review}"
    
#     def image_tag_review(self):
#         # Возвращаем все изображения, связанные с продуктом
#         return self.review.image.all()
#     image_tag_review.short_description = "Изображение"
    
#     class Meta:
#         verbose_name = 'Изображение отзыва'
#         verbose_name_plural = 'Изображения отзывов'




class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = ProcessedImageField(
        upload_to=review_image_upload_path,
        processors=[ResizeToFit(500, 500, upscale=False)],  # Квадратные миниатюры, как в шаблоне
        format='WEBP',
        options={'quality': 95, 'optimize': True}, 
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size,
            validate_image_mime_type,  # Новый валидатор
        ],
        blank=True,
        null=True, verbose_name='Изображение', db_index=True,
    )

    def clean(self):
        existing_images = self.review.images.exclude(pk=self.pk).count()  # Исключаем текущий объект
        if existing_images >= 5:
            raise ValidationError('Максимум 5 изображений на отзыв.')



    def __str__(self):
        return f"{self.review}"
    
    def image_tag_review(self):
        # Возвращаем все изображения, связанные с продуктом
        return self.review.image.all()
    image_tag_review.short_description = "Изображение"
    
    class Meta:
        verbose_name = 'Изображение отзыва'
        verbose_name_plural = 'Изображения отзывов'