from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Size,Product,ProductImage,ProductPrice,News,SizeTable,Uslovie_firm,Politica_firm,ImageSliderHome,DeliveryInfo,Review,ReviewImage
from django.utils.safestring import mark_safe
from slugify import slugify
from django.utils.html import format_html
from django import forms





class ProductPriceAdminForm(forms.ModelForm):
    new_sale_price = forms.DecimalField(label='Новая цена продажи', max_digits=20, decimal_places=0, required=False)
    new_purchase_price = forms.DecimalField(label='Новая цена закупки', max_digits=20, decimal_places=0, required=False)
    new_old_price = forms.DecimalField(label='Новая старая цена', max_digits=20, decimal_places=0, required=False)

    class Meta:
        model = ProductPrice
        fields = '__all__'

    def save(self, commit=True):
        # Получаем текущий объект продукта
        product = self.instance.product

        # Обновляем цены для всех размеров продукта
        # Сначала обновляем саму запись, к которой относится форма
        if self.cleaned_data['new_sale_price'] is not None:
            self.instance.price = self.cleaned_data['new_sale_price']
        if self.cleaned_data['new_purchase_price'] is not None:
            self.instance.zacup_price = self.cleaned_data['new_purchase_price']
        if self.cleaned_data['new_old_price'] is not None:
            self.instance.old_price = self.cleaned_data['new_old_price']

        # Сохраняем текущую запись
        if commit:
            self.instance.save()

        # Обновляем остальные записи
        for price_entry in product.product_prices.exclude(id=self.instance.id):  # Исключаем текущую запись
            if self.cleaned_data['new_sale_price'] is not None:
                price_entry.price = self.cleaned_data['new_sale_price']
            if self.cleaned_data['new_purchase_price'] is not None:
                price_entry.zacup_price = self.cleaned_data['new_purchase_price']
            if self.cleaned_data['new_old_price'] is not None:
                price_entry.old_price = self.cleaned_data['new_old_price']

            # Сохраняем обновленную запись
            price_entry.save()
    
        return super().save(commit)




@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('title',)  # Отображение названия размера в админке
    search_fields = ['title']  # Определяем поле для поиска



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_tag',)
    fields = ('image_tag', 'image')

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width='75'>")
        return 'Нет фото'
    image_tag.short_description = "Фото"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product','image',)


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product','size', 'price','old_price','zacup_price',)



class ProductPriceInline(admin.TabularInline):
    form = ProductPriceAdminForm
    model = ProductPrice
    extra = 1  # Количество пустых форм для добавления новых записей
    fields = ('size', 'price','zacup_price','old_price','new_sale_price', 'new_purchase_price', 'new_old_price')
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductPriceInline]  # Подключаем инлайн для изображений
    list_display = ('get_image','title', 'article_number','stock','description', 'unit','get_prices_and_sizes','get_zacup_prices_and_sizes','get_old_prices_and_sizes','is_hidden','category','mesto')  # Отображение полей продукта в админке
    list_filter = ('is_hidden','category','created','updated','mesto')
    prepopulated_fields = {'slug':('title','article_number',)}
    search_fields = ['title','article_number','description']  # Позволяет искать продукты по названию
    list_editable = ['is_hidden','mesto']
    actions = ['hide_products', 'show_products','duplicate_product']
    list_display_links=['get_image','title',]


    def get_prices_and_sizes(self, obj):
        prices = obj.product_prices.select_related('size')  # Оптимизация запросов
        price_size_list = [f"{price.size.title if price.size else 'Без размера'} - {price.price}" for price in prices]
        if price_size_list:
            return format_html('<br>'.join(price_size_list))  # Используем <br> для разделения строк
        return 'Нет цен'
    
    get_prices_and_sizes.short_description = 'Размер и цена'  # Размер и цена:

    def get_zacup_prices_and_sizes(self, obj):
        prices = obj.product_prices.select_related('size')  # Оптимизация запросов
        price_list = [f"{price.zacup_price}" for price in prices]  # Выводим только цену закупки

        if price_list:
            return format_html('<br>'.join(price_list))  # Используем <br> для разделения строк
        return 'Нет цен'

    get_zacup_prices_and_sizes.short_description = 'Цена закупки'  # Цена закупки:

    def get_old_prices_and_sizes(self, obj):
        prices = obj.product_prices.select_related('size')  # Оптимизация запросов
        price_list = [f"{price.old_price}" for price in prices]  # Выводим только старую цену

        if price_list:
            return format_html('<br>'.join(price_list))  # Используем <br> для разделения строк
        return 'Нет цен'

    get_old_prices_and_sizes.short_description = 'Старая цена'  # Старая цена:

    

    def duplicate_product(self, request, queryset):
        for product in queryset:
            print(f"Дублируем продукт: {product.title}")
            try:
                # Получаем цены для исходного продукта
                prices = product.product_prices.all()
                print(f"Количество цен для исходного продукта {product.title}: {prices.count()}")

                # Создаем новый продукт
                new_product = product
                new_product.pk = None  # Сбрасываем первичный ключ
                new_product.title = f"{product.title}"
                new_product.slug = self.generate_unique_slug(product.title, product.article_number)
                new_product.article_number = self.generate_unique_article_number(product.article_number)
                new_product.save()
                print(f"Создан новый продукт: {new_product.title} с slug: {new_product.slug} и article_number: {new_product.article_number}")

                # Копируем цены из исходного продукта
                for price in prices:
                    print(f"Копируем цену: {price.price} для размера: {price.size.title}")
                    new_price = ProductPrice()  # Создаем новый объект цены
                    new_price.price = price.price  # Копируем цену
                    new_price.size = price.size  # Копируем размер
                    new_price.zacup_price = price.zacup_price  # Копируем zacup_price
                    new_price.old_price = price.old_price  # Копируем old_price
                    new_price.product = new_product  # Привязываем цену к новому продукту
                    new_price.save()  # Сохраняем новый объект
                    print(f"Создана новая цена: {new_price.price} для продукта: {new_product.title} с размером: {new_price.size.title}")

            except Exception as e:
                print(f"Ошибка при дублировании продукта {product.title}: {e}")

    def generate_unique_slug(self, title, article_number):
        base_slug = slugify(f"{title}-{article_number}")  # Создаем базовый slug
        unique_slug = base_slug
        counter = 1
        while Product.objects.filter(slug=unique_slug).exists():  # Проверяем на уникальность
            unique_slug = f"{base_slug}-{counter}"  # Добавляем счетчик, если slug уже существует
            counter += 1
        return unique_slug

    def generate_unique_article_number(self, article_number):
        # Преобразуем article_number в строку, чтобы избежать проблем с нечисловыми значениями
        base_article_number = int(article_number)  # Приводим к числу
        unique_article_number = base_article_number
        counter = 1
        while Product.objects.filter(article_number=unique_article_number).exists():  # Проверяем на уникальность
            unique_article_number = base_article_number + counter  # Добавляем счетчик как число
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


    def get_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
        return 'Нет фото'
    get_image.short_description = "Фото"



@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title','description','created',)



@admin.register(SizeTable)
class SizeTableAdmin(admin.ModelAdmin):
    list_display = ('title','image',)



@admin.register(Uslovie_firm)
class Uslovie_firmAdmin(admin.ModelAdmin):
    list_display = ('title','description',)


@admin.register(DeliveryInfo)
class DeliveryInfoAdmin(admin.ModelAdmin):
    list_display = ('title','description',)



@admin.register(Politica_firm)
class Politica_firmAdmin(admin.ModelAdmin):
    list_display = ('title','description',)



@admin.register(ImageSliderHome)
class ImageSliderHome(admin.ModelAdmin):
    list_display = ('image',)



@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review','image',)


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ('image_tag',)
    fields = ('image_tag', 'image')

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width='75'>")
        return 'Нет фото'
    image_tag.short_description = "Фото"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewImageInline]
    list_display = ('user','content','get_image_review','kachestvo_rating','obsluga_rating','sroki_rating','created_at')

    def get_queryset(self, request):
        # Используем prefetch_related для загрузки связанных изображений
        qs = super().get_queryset(request)
        return qs.prefetch_related('images')

    def get_image_review(self, obj):
        images = obj.images.all()  # Получаем все изображения, связанные с отзывом
        if images.exists():
            # Создаем строку с HTML-кодом для отображения всех изображений
            return mark_safe(" ".join([f"<img src='{image.image.url}' width='50'>" for image in images]))
        return 'Нет фото'
    
    get_image_review.short_description = "Изображение"



admin.site.register(Category,DraggableMPTTAdmin,
    list_display=('tree_actions','indented_title','image'),
    list_display_links=('indented_title',),
    prepopulated_fields = {'slug':('name',)})