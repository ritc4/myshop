from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Size,Product,ProductImage
from django.utils.safestring import mark_safe
from slugify import slugify

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('title',)  # Отображение названия размера в админке
    search_fields = ['title']  # Определяем поле для поиска



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Количество пустых форм для добавления новых изображений
    readonly_fields = ('image_tag',)  # Делаем поле для изображения только для чтения
    fields = ('image_tag', 'image')  # Указываем, какие поля отображать


    def image_tag(self, obj):
        # Получаем первое изображение, если оно существует
        image = obj.image  # Здесь используем related_name 'images'
        if image:
            return mark_safe(f"<img src='{image.url}' width='75'>")
        else:
            return 'Нет фото' 

    image_tag.short_description = 'Фото'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image',)

    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]  # Подключаем инлайн для изображений
    list_display = ('get_image','title', 'article_number', 'stock', 'unit', 'is_hidden', 'get_sizes_display','price','category','created','updated','mesto')  # Отображение полей продукта в админке
    list_filter = ('is_hidden','category','created','updated','mesto')
    prepopulated_fields = {'slug':('title','article_number',)}
    filter_horizontal = ('size',)  # Используем горизонтальный фильтр для выбора 
    search_fields = ['title','article_number',]  # Позволяет искать продукты по названию
    list_editable = ['price', 'is_hidden','mesto',]
    actions = ['hide_products', 'show_products','duplicate_product',]


    def duplicate_product(self, request, queryset):
        for product in queryset:
            product.pk = None  # Сбрасываем первичный ключ, чтобы создать новый объект
            product.title = f"Копия {product.title}"  # Изменяем название
            product.slug = self.generate_unique_slug(product.title, product.article_number)  # Генерируем уникальный slug
            product.article_number = self.generate_unique_article_number(product.article_number)  # Генерируем новый уникальный артикул
            product.save()  # Сохраняем новый объект
        self.message_user(request, "Товары успешно скопированы.")

    def generate_unique_slug(self, title, article_number):
        base_slug = slugify(f"{title}-{article_number}")  # Создаем базовый slug
        unique_slug = base_slug
        counter = 1
        while Product.objects.filter(slug=unique_slug).exists():  # Проверяем на уникальность
            unique_slug = f"{base_slug}-{counter}"  # Добавляем счетчик, если slug уже существует
            counter += 1
        return unique_slug

    def generate_unique_article_number(self, article_number):
        # Преобразуем article_number в число
        unique_article_number = int(article_number)
        counter = 1
        while Product.objects.filter(article_number=unique_article_number).exists():  # Проверяем на уникальность
            unique_article_number = int(article_number) + counter  # Увеличиваем на 1
            counter += 1
        return unique_article_number
    
    duplicate_product.short_description = "Скопировать выбранные товары"



    def hide_products(self, request, queryset):
        queryset.update(is_hidden=True)  # Скрываем выбранные товары
        self.message_user(request, f"{queryset.count()} товаров успешно скрыто.")
    hide_products.short_description = "Скрыть выбранные товары"  # Описание действия

    def show_products(self, request, queryset):
        queryset.update(is_hidden=False)  # Показываем выбранные товары
        self.message_user(request, f"{queryset.count()} товаров успешно показано.")
    show_products.short_description = "Показать выбранные товары"  # Описание действия

    def get_sizes_display(self, obj):
        return ", ".join([size.title for size in obj.size.all()]) 
    get_sizes_display.short_description = 'Размер'  # Название колонки в админке


    def get_image(self, obj):
        # Получаем первое изображение, если оно существует
        first_image = obj.images.first()  # Здесь используем related_name 'images'
        if first_image:
            return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
        else:
            return 'Нет фото' 

    get_image.short_description = 'Фото'


admin.site.register(Category,DraggableMPTTAdmin,
    list_display=('tree_actions','indented_title','image'),
    list_display_links=('indented_title',),
    prepopulated_fields = {'slug':('name',)})