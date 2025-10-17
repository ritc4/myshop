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

        # Обновляем текущую запись
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
        prices_to_update = []
        for price_entry in product.product_prices.exclude(id=self.instance.id):  # Исключаем текущую запись
            if self.cleaned_data['new_sale_price'] is not None:
                price_entry.price = self.cleaned_data['new_sale_price']
            if self.cleaned_data['new_purchase_price'] is not None:
                price_entry.zacup_price = self.cleaned_data['new_purchase_price']
            if self.cleaned_data['new_old_price'] is not None:
                price_entry.old_price = self.cleaned_data['new_old_price']

            prices_to_update.append(price_entry)

        # Обновляем все записи в одном запросе
        if prices_to_update:
            ProductPrice.objects.bulk_update(prices_to_update, ['price', 'zacup_price', 'old_price'])

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
        if obj.image and obj.image.file:  # Добавлена проверка на .file
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
    fields = ('size', 'price','zacup_price','old_price','new_sale_price', 'new_purchase_price','new_old_price')

    
    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('product').prefetch_related('size')  # Это загружает размер вместе с ценами
        return queryset
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductPriceInline]  # Подключаем инлайн для изображений
    list_display = ('get_image','title', 'article_number','stock','description','display_price','display_zacup_price','display_old_price', 'unit','is_hidden','category','mesto')  # Отображение полей продукта в админке
    list_filter = ('is_hidden','category','created','updated','mesto')
    prepopulated_fields = {'slug':('title','article_number',)}
    search_fields = ['title','article_number','description']  # Позволяет искать продукты по названию
    list_editable = ['is_hidden','mesto']
    actions = ['hide_products', 'show_products','duplicate_product']
    list_display_links=['get_image','title',]



    def get_queryset(self, request):
        # Используем prefetch_related для оптимизации запросов к ценам и размерам
        queryset = super().get_queryset(request).prefetch_related('product_prices','images','product_prices__size')
        return queryset


    def get_prices_info(self, obj):
        prices = obj.product_prices.all()
        price_info_list = []

        for price in prices:
            size_title = price.size.title if price.size else 'Без размера'
            price_info_list.append({
                'size': size_title,
                'price': price.price,
                'zacup_price': price.zacup_price,
                'old_price': price.old_price,
            })

        return price_info_list

    def display_prices(self, obj, price_type):
        price_info_list = self.get_prices_info(obj)
        if price_info_list:
            return format_html('<br>'.join([f"{info['size']} - {info[price_type]}" for info in price_info_list]))
        return 'Нет цен'

    def display_price(self, obj):
        return self.display_prices(obj, 'price')

    def display_zacup_price(self, obj):
        return self.display_prices(obj, 'zacup_price')

    def display_old_price(self, obj):
        return self.display_prices(obj, 'old_price')

    # Устанавливаем заголовки для колонок
    display_price.short_description = 'Обычная цена'
    display_zacup_price.short_description = 'Закупочная цена'
    display_old_price.short_description = 'Старая цена'

    

    def duplicate_product(self, request, queryset):
        for product in queryset:
            # print(f"Дублируем продукт: {product.title}")
            try:
                # Получаем цены для исходного продукта
                prices = product.product_prices.all()
                # print(f"Количество цен для исходного продукта {product.title}: {prices.count()}")

                # Создаем новый продукт
                new_product = product
                new_product.pk = None  # Сбрасываем первичный ключ
                new_product.title = f"{product.title}"
                new_product.slug = self.generate_unique_slug(product.title, self.generate_unique_article_number(product.article_number))
                new_product.article_number = self.generate_unique_article_number(product.article_number)
                new_product.save()
                # print(f"Создан новый продукт: {new_product.title} с slug: {new_product.slug} и article_number: {new_product.article_number}")

                # Копируем цены из исходного продукта
                for price in prices:
                    # print(f"Копируем цену: {price.price} для размера: {price.size.title}")
                    new_price = ProductPrice()  # Создаем новый объект цены
                    new_price.price = price.price  # Копируем цену
                    new_price.size = price.size  # Копируем размер
                    new_price.zacup_price = price.zacup_price  # Копируем zacup_price
                    new_price.old_price = price.old_price  # Копируем old_price
                    new_price.product = new_product  # Привязываем цену к новому продукту
                    new_price.save()  # Сохраняем новый объект
                    # print(f"Создана новая цена: {new_price.price} для продукта: {new_product.title} с размером: {new_price.size.title}")

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
        count = queryset.update(is_hidden=True)  # Скрываем выбранные товары
        self.message_user(request, f"{count} товаров успешно скрыто.")
    hide_products.short_description = "Скрыть выбранные товары"  # Описание действия

    def show_products(self, request, queryset):
        count = queryset.update(is_hidden=False)  # Показываем выбранные товары
        self.message_user(request, f"{count} товаров успешно показано.")
    show_products.short_description = "Показать выбранные товары"  # Описание действия
    


    # def get_image(self, obj):
    #     first_image = obj.images.first()
    #     if first_image:
    #         return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
    #     return 'Нет фото'
    # get_image.short_description = "Фото"

    def get_image(self, obj):
        images = obj.images.all()  # Уже предзагружены благодаря prefetch_related
        if images:
            first_image = images[0]
            if first_image.image and first_image.image.file:  # Проверка на наличие файла
                return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
        return 'Нет фото'
    get_image.short_description = 'Фото товара'



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
    list_display = ('id','image', )



@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review','image',)

    def get_queryset(self, request):
        # Используем prefetch_related для загрузки связанных изображений
        qs = super().get_queryset(request)
        return qs.select_related('review').prefetch_related('review__user')


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ('image_tag',)
    fields = ('image_tag', 'image')

    def get_queryset(self, request):
        # Используем prefetch_related для загрузки связанных изображений
        qs = super().get_queryset(request)
        return qs.select_related('review').prefetch_related('review__user')

    def image_tag(self, obj):
        if obj.image and obj.image.file:  # Добавлена проверка на .file
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
        return qs.select_related('user').prefetch_related('images')

    def get_image_review(self, obj):
        images = obj.images.all()  # Предзагружены благодаря prefetch_related
        if images.exists():
            img_tags = []
            for image in images:
                if image.image and image.image.file:  # Проверка для каждого изображения
                    img_tags.append(f"<img src='{image.image.url}' width='50'>")
            if img_tags:
                return mark_safe(" ".join(img_tags))
        return 'Нет фото'
    get_image_review.short_description = "Изображение"



admin.site.register(Category,DraggableMPTTAdmin,
    list_display=('tree_actions','indented_title','image'),
    list_display_links=('indented_title',),
    prepopulated_fields = {'slug':('name',)})