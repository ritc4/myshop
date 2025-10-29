from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Size,Product,ProductImage,ProductPrice,News,SizeTable,Uslovie_firm,Politica_firm,ImageSliderHome,DeliveryInfo,Review,ReviewImage
from django.utils.safestring import mark_safe
from slugify import slugify
from django.utils.html import format_html
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ngettext
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe




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
    # form = ProductPriceAdminForm
    model = ProductPrice
    extra = 1  # Количество пустых форм для добавления новых записей
    fields = ('size', 'price','zacup_price','old_price')

    
    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('product').prefetch_related('size')  # Это загружает размер вместе с ценами
        return queryset



# Форма для массового обновления цен (исправлено: zacup_price вместо zakup_price)
class BulkUpdatePricesForm(forms.Form):
    price = forms.DecimalField(label='Новая цена продажи', required=False, max_digits=10, decimal_places=0, help_text='Оставьте пустым, чтобы не менять')
    old_price = forms.DecimalField(label='Новая старая цена', required=False, max_digits=10, decimal_places=0, help_text='Оставьте пустым, чтобы не менять')
    zacup_price = forms.DecimalField(label='Новая цена закупки', required=False, max_digits=10, decimal_places=0, help_text='Оставьте пустым, чтобы не менять')



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductPriceInline]  # Подключаем инлайн для изображений
    list_display = ('get_image','title', 'article_number','stock','display_description','display_price','display_zacup_price','display_old_price', 'unit','is_hidden','category','mesto')  # Отображение полей продукта в админке
    list_filter = ('is_hidden','category','created','updated','mesto')
    prepopulated_fields = {'slug':('title','article_number',)}
    search_fields = ['title','article_number','display_description',]  # Позволяет искать продукты по названию
    list_editable = ['is_hidden','mesto']
    actions = ['hide_products', 'show_products','duplicate_product','change_category','bulk_update_prices'] 
    list_display_links=['get_image','title',]


    def display_description(self, obj):
        # Рендерим HTML из description, чтобы <br /> превращались в реальные переносы строк
        return mark_safe(obj.description) if obj.description else ''
    
    display_description.short_description = 'Описание'



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


    # Новый action для массового обновления цен
    # Исправленный action для массового обновления цен
    def bulk_update_prices(self, request, queryset):
        if 'apply' in request.POST:
            form = BulkUpdatePricesForm(request.POST)
            if form.is_valid():
                updates = {k: v for k, v in form.cleaned_data.items() if v is not None}
                if updates:
                    updated_count = 0
                    for product in queryset:
                        # Обновляем все связанные ProductPrice для продукта
                        count = ProductPrice.objects.filter(product=product).update(**updates)
                        updated_count += count
                    if updated_count > 0:
                        self.message_user(request, f'Обновлено {updated_count} записей цен для {queryset.count()} продуктов.', messages.SUCCESS)
                    else:
                        self.message_user(request, 'Не найдено записей для обновления (возможно, продукты без размеров).', messages.WARNING)
                else:
                    self.message_user(request, 'Не указаны поля для обновления.', messages.WARNING)
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BulkUpdatePricesForm()
        return render(request, 'admin/bulk_update_prices.html', {
            'title': 'Массовое обновление цен',
            'form': form,
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })
    bulk_update_prices.short_description = 'Массово обновить цены'

    

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
    


    def get_image(self, obj):
        images = obj.images.all()  # Уже предзагружены благодаря prefetch_related
        if images:
            first_image = images[0]
            if first_image.image and first_image.image.file:  # Проверка на наличие файла
                return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
        return 'Нет фото'
    get_image.short_description = 'Фото товара'



    # Новое действие для изменения категории
    def change_category(self, request, queryset):
        if 'apply' in request.POST:
            category_id = request.POST.get('category')
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    updated = queryset.update(category=category)
                    self.message_user(
                        request,
                        ngettext(
                            '%d продукт был успешно перемещен в категорию "%s".',
                            '%d продуктов были успешно перемещены в категорию "%s".',
                            updated,
                        ) % (updated, category.name),
                        messages.SUCCESS,
                    )
                except Category.DoesNotExist:
                    self.message_user(request, "Выбранная категория не существует.", messages.ERROR)
            else:
                self.message_user(request, "Категория не выбрана.", messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())

        # Отображаем форму выбора категории
        categories = Category.objects.all()  # Получаем все категории (MPTT дерево)
        return render(request, 'admin/change_category.html', {
            'title': 'Изменить категорию для выбранных продуктов',
            'products': queryset,
            'categories': categories,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })

    change_category.short_description = "Изменить категорию выбранных товаров"

    # Добавляем URL для промежуточной страницы (опционально, для расширения)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change-category/', self.admin_site.admin_view(self.change_category_view), name='change_category'),
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def change_category_view(self, request):
        # Если нужно, можно реализовать отдельную view для выбора категории
        # Но для простоты, действие change_category уже обрабатывает форму
        pass



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