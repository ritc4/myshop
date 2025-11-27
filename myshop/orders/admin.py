# from django.contrib import admin
# from .models import Order, OrderItem, DeliveryMethod, Discount
# from django.utils.safestring import mark_safe
# from django.db.models import Q, Sum
# from django.urls import reverse, path
# from django.shortcuts import render
# from django.utils import timezone
# from datetime import timedelta
# from home.models import ProductPrice, Size, Product
# from django import forms
# from django.contrib.admin.widgets import ForeignKeyRawIdWidget 
# from django.urls.exceptions import NoReverseMatch


# def order_pdf(obj):
#     url = reverse('orders:admin_order_pdf', args=[obj.id]) 
#     return mark_safe(f'<a href="{url}">Чек</a>')
# order_pdf.short_description = 'Чеки'



# # Кастомный виджет без запросов на label/URL (по оригинальной логике Django)
# class CustomProductPriceRawIdWidget(ForeignKeyRawIdWidget):
#     def label_and_url_for_value(self, value):
#         if value:
#             if self.rel and hasattr(self.rel, 'model'):
#                 opts = self.rel.model._meta
#                 try:
#                     # Строим URL как в оригинале: admin:app_label:model_change с pk в args
#                     url = reverse(
#                         f'{opts.app_label}:{opts.model_name}_change',
#                         args=[value]
#                     )
#                     label = f'ID: {value}'
#                 except NoReverseMatch:
#                     # Если URL не найден (например, модель не зарегистрирована в админе), пустой URL
#                     url = ''
#                     label = f'ID: {value}'
#             else:
#                 # Fallback, если rel не установлен
#                 url = ''
#                 label = f'ID: {value}'
#             return label, url
#         return '', ''

# class OrderItemInlineForm(forms.ModelForm):
#     class Meta:
#         model = OrderItem
#         fields = '__all__'

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     form = OrderItemInlineForm
#     raw_id_fields = ['product_price']
#     extra = 1
#     fields = ['product_image', 'product_price', 'product_article_number', 'size_title', 'product_mesto', 'product_zacup_price', 'quantity', 'price', 'is_price_custom', 'get_cost']
#     readonly_fields = ['product_image', 'product_article_number', 'size_title', 'product_mesto', 'product_zacup_price', 'get_cost']

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'product_price':
#             kwargs['widget'] = CustomProductPriceRawIdWidget(db_field.remote_field, self.admin_site)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     def get_formset(self, request, obj=None, **kwargs):
#         formset = super().get_formset(request, obj, **kwargs)
#         # Предзагрузка queryset для product_price (остается — помогает рендеру)
#         # Но теперь clean() formset не будет запускать N SELECT, а один batch
#         formset.form.base_fields['product_price'].queryset = (
#             ProductPrice.objects.select_related('product', 'size')
#             .prefetch_related('product__images')
#         )
#         return formset

#     def get_queryset(self, request):
#         # Предзагрузка для readonly_fields
#         queryset = super().get_queryset(request).select_related(
#             'product_price__product', 'product_price__size'
#         ).prefetch_related(
#             'product_price__product__images',
#             'product_price'
#         )
#         return queryset

    
#     def product_image(self, obj):
#         if obj.product_price and obj.product_price.product:
#             images = obj.product_price.product.images.all()  # prefetch кэш
#             if images:
#                 image_url = images[0].image.url
#                 return mark_safe(f'<img src="{image_url}" width="50" height="50" />')
#         return 'Фото отсутствует'
#     product_image.short_description = 'Фото товара'

#     def product_title(self, obj):
#         # Добавлена полная проверка на None, чтобы избежать AttributeError
#         if obj.product_price and obj.product_price.product and obj.product_price.product.title:
#             return obj.product_price.product.title
#         return 'Товар отсутствует'
#     product_title.short_description = 'Товар'
    
#     def product_article_number(self, obj):
#         if obj.product_price and obj.product_price.product and obj.product_price.product.article_number:
#             return obj.product_price.product.article_number
#         return 'Артикул не указан'
#     product_article_number.short_description = 'Артикул'
    
#     def size_title(self, obj):
#         # Добавлена полная проверка на None
#         if obj.product_price and obj.product_price.size and obj.product_price.size.title:
#             return obj.product_price.size.title
#         return 'Размер отсутствует'
#     size_title.short_description = 'Размер'

#     def product_mesto(self, obj):
#         if obj.product_price and obj.product_price.product and obj.product_price.product.mesto:
#             return obj.product_price.product.mesto
#         return 'Место не указано'
#     product_mesto.short_description = 'Место'
    

#     class Media:
#         js = ('admin/js/vendor/jquery/jquery.min.js', 'my_js/dynamic_orderitem_fields.js',)

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'id',
#         'first_name_last_name',
#         'email',
#         'paid',
#         'status',
#         'phone',
#         'region',
#         'city',
#         'address',
#         'postal_code',   
#         'get_total_cost',
#         'get_total_zakup_cost',
#         order_pdf, 
#     ]
    
#     list_editable = ['paid', 'status']
#     readonly_fields = ['get_total_zakup_cost', 'get_total_cost']
#     list_filter = ['paid', 'created', 'updated'] 
#     inlines = [OrderItemInline]
#     search_fields = ['items__product_price__product__article_number', 'first_name_last_name', 'email', 'phone', 'city']  # Обновлено: используем product_price__product
#     list_display_links = ['id', 'first_name_last_name'] 

    
#     def get_queryset(self, request):
#         # Загружаем связанные модели для оптимизации запросов
#         queryset = super().get_queryset(request).select_related('delivery_method', 'discount').prefetch_related(
#             'items__product_price__product',
#             'items__product_price__size',
#         )
#         return queryset

#     def get_delivery_price(self, obj):
#         # Проверяем, установлен ли способ доставки
#         if obj.delivery_method:
#             # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
#             return obj.price_delivery if obj.price_delivery is not None else "Не указано"
#         return "Не указано"  # Если способ доставки не указан

#     get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки
    

#     def get_total_zakup_cost(self, obj):
#         total_cost = sum(
#             (item.product_price.zacup_price or 0) * item.quantity 
#             for item in obj.items.all() if item.product_price
#         )
#         return total_cost
#     get_total_zakup_cost.short_description = 'Общая закупочная стоимость'  # Заголовок для отображения

#     def get_search_results(self, request, queryset, search_term):
#         if search_term:
#             queryset = queryset.filter(
#                 Q(items__product_price__product__article_number__icontains=search_term) | 
#                 Q(first_name_last_name__icontains=search_term) | 
#                 Q(email__icontains=search_term) |
#                 Q(phone__icontains=search_term)
#             ).distinct()
#         return super().get_search_results(request, queryset, search_term)
    

#     change_list_template = "admin/orders/order/change_list.html"  # Укажите свой шаблон

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('top_client/', self.admin_site.admin_view(self.top_client_view), name='top_client'),
#         ]
#         return custom_urls + urls

#     def top_client_view(self, request):
#         now = timezone.now()

#         # Получаем все заказы с оптимизацией
#         orders = self.get_queryset(request)  # Используем get_queryset для загрузки заказов
        
#         # Создаем словарь для хранения информации о клиентах
#         client_data = {}

#         for order in orders:
#             # print(f"Заказ ID: {order.id}, Email: {order.email}, Сумма: {order.get_total_cost()}")
#             email = order.email

#             # Проверяем, существует ли email в словаре
#             if email not in client_data:
#                 client_data[email] = {
#                     'first_name_last_name': order.first_name_last_name,
#                     'phone': order.phone,
#                     'city': order.city,
#                     'total_orders': 0,
#                     'total_spent': 0,
#                     'last_purchase': order.created,
#                 }

#             # Обновляем информацию о клиенте
#             client_data[email]['total_orders'] += 1
#             client_data[email]['total_spent'] += order.get_total_cost()  # Используем метод get_total_cost
#             client_data[email]['last_purchase'] = max(client_data[email]['last_purchase'], order.created)


#         # Преобразуем данные в список и сортируем по total_spent
#         top_clients = sorted(client_data.items(), key=lambda x: x[1]['total_spent'], reverse=True)[:100]

#         # Рассчитываем средний чек и период
#         for email, client in top_clients:
#             client['average_check'] = (
#                 client['total_spent'] / client['total_orders'] 
#                 if client['total_orders'] > 0 else 0
#             )
#             client['average_period'] = (
#                 (now - client['last_purchase']).days // client['total_orders'] 
#                 if client['total_orders'] > 0 else 0
#             )

#         return render(request, 'admin/orders/order/top_client.html', {
#             'top_clients': top_clients,
#         })

#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['top_client_url'] = reverse('admin:top_client')
#         return super().changelist_view(request, extra_context=extra_context)

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ['order', 'product_title', 'price', 'is_price_custom', 'quantity', 'size_title']  # Обновлено: используем методы для отображения
#     change_list_template = "admin/orders/orderitem/change_list.html"  # Укажите свой шаблон

#     def product_title(self, obj):
#         if obj.product_price and obj.product_price.product:
#             return obj.product_price.product.title
#         return 'Нет товара'
#     product_title.short_description = 'Товар'

#     def size_title(self, obj):
#         if obj.product_price and obj.product_price.size:
#             return obj.product_price.size.title
#         return 'Размер не указан'
#     size_title.short_description = 'Размер'

#     def get_queryset(self, request):
#         # Загружаем связанные модели для оптимизации запросов
#         queryset = super().get_queryset(request)
#         return queryset.select_related('product_price__product', 'product_price__size', 'order')
    
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('top_product/', self.admin_site.admin_view(self.top_products_view), name='top_product'),
#         ]
#         return custom_urls + urls

#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['top_product_url'] = reverse('admin:top_product')
#         return super().changelist_view(request, extra_context=extra_context)

#     def top_products_view(self, request):
#         now = timezone.now()

#         # Определяем временные рамки для различных периодов
#         period_mapping = {
#             '1_month': now - timedelta(days=30),
#             '3_months': now - timedelta(days=90),
#             '1_year': now - timedelta(days=365),
#         }

#         # Получаем все заказы за последний год и группируем по продуктам
#         all_orders = (
#             OrderItem.objects.filter(order__created__gte=period_mapping['1_year'])
#             .select_related('product_price__product', 'product_price__size')  # Обновлено: select_related через product_price
#             .values('product_price__product__title', 'product_price__product__article_number')  # Обновлено: используем product_price__product
#             .annotate(total_quantity=Sum('quantity'))  # Суммируем количество
#         )

#         # Группируем данные по периодам
#         top_products_month = (
#             all_orders.filter(order__created__gte=period_mapping['1_month'])
#             .order_by('-total_quantity')[:60]
#         )

#         top_products_three_months = (
#             all_orders.filter(order__created__gte=period_mapping['3_months'])
#             .order_by('-total_quantity')[:60]
#         )

#         top_products_year = (
#             all_orders.order_by('-total_quantity')[:60]
#         )

#         return render(request, 'admin/orders/orderitem/top_product.html', {
#             'top_products_month': top_products_month,
#             'top_products_three_months': top_products_three_months,
#             'top_products_year': top_products_year,
#         })

# @admin.register(DeliveryMethod)
# class DeliveryMethodAdmin(admin.ModelAdmin):
#     list_display = [
#         'title'
#     ]

# @admin.register(Discount)
# class DiscountAdmin(admin.ModelAdmin):
#     list_display = ('discount_type', 'discount_value')







from django.contrib import admin
from .models import Order, OrderItem, DeliveryMethod, Discount
from django.utils.safestring import mark_safe
from django.db.models import Q, Sum
from django.urls import reverse, path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from home.models import ProductPrice, Size, Product
from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget 
from django.urls.exceptions import NoReverseMatch
from django.db.models import Sum, F


def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id]) 
    return mark_safe(f'<a href="{url}">Чек</a>')
order_pdf.short_description = 'Чеки'



# Кастомный виджет без запросов на label/URL (по оригинальной логике Django)
class CustomProductPriceRawIdWidget(ForeignKeyRawIdWidget):
    def label_and_url_for_value(self, value):
        if value:
            if self.rel and hasattr(self.rel, 'model'):
                opts = self.rel.model._meta
                try:
                    # Строим URL как в оригинале: admin:app_label:model_change с pk в args
                    url = reverse(
                        f'{opts.app_label}:{opts.model_name}_change',
                        args=[value]
                    )
                    label = f'ID: {value}'
                except NoReverseMatch:
                    # Если URL не найден (например, модель не зарегистрирована в админе), пустой URL
                    url = f'ID: {value}'
                    label = f'ID: {value}'
                return label, url
            else:
                # Fallback, если rel не установлен
                url = ''
                label = f'ID: {value}'
            return label, url
        return '', ''

class OrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemInlineForm
    raw_id_fields = ['product_price']
    extra = 1
    fields = ['product_image', 'product_price', 'product_article_number', 'size_title', 'product_mesto', 'product_zacup_price', 'quantity', 'price', 'is_price_custom', 'get_cost']
    readonly_fields = ['product_image', 'product_article_number', 'size_title', 'product_mesto', 'product_zacup_price', 'get_cost']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product_price':
            kwargs['widget'] = CustomProductPriceRawIdWidget(db_field.remote_field, self.admin_site)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Предзагрузка queryset для product_price (остается — помогает рендеру)
        # Но теперь clean() formset не будет запускать N SELECT, а один batch
        formset.form.base_fields['product_price'].queryset = (
            ProductPrice.objects.select_related('product', 'size')
            .prefetch_related('product__images')
        )
        return formset

    def get_queryset(self, request):
        # Предзагрузка для readonly_fields
        queryset = super().get_queryset(request).select_related(
            'product_price__product', 'product_price__size'
        ).prefetch_related(
            'product_price__product__images',
            'product_price'
        )
        return queryset

    
    def product_image(self, obj):
        # Изображение всегда из связанного продукта, snapshots не помогут
        if obj and obj.product_price and obj.product_price.product:
            images = obj.product_price.product.images.all()  # prefetch кэш
            if images:
                image_url = images[0].image.url
                return mark_safe(f'<img src="{image_url}" width="50" height="50" />')
        return 'Фото отсутствует'
    product_image.short_description = 'Фото товара'

    def product_title(self, obj):
        # Приоритет: product_snapshot, fallback к product_price
        if obj and obj.product_snapshot:
            return obj.product_snapshot
        elif obj and obj.product_price and obj.product_price.product and obj.product_price.product.title:
            return obj.product_price.product.title
        return 'Товар отсутствует'
    product_title.short_description = 'Товар'
    
    def product_article_number(self, obj):
        # Приоритет: article_snapshot, fallback к product_price
        if obj and obj.article_snapshot:
            return obj.article_snapshot
        elif obj and obj.product_price and obj.product_price.product and obj.product_price.product.article_number:
            return obj.product_price.product.article_number
        return 'Артикул не указан'
    product_article_number.short_description = 'Артикул'
    
    def size_title(self, obj):
        # Приоритет: size_snapshot, fallback к product_price
        if obj and obj.size_snapshot:
            return obj.size_snapshot
        elif obj and obj.product_price and obj.product_price.size and obj.product_price.size.title:
            return obj.product_price.size.title
        return 'Размер отсутствует'
    size_title.short_description = 'Размер'

    def product_mesto(self, obj):
        # Приоритет: mesto_snapshot, fallback к product_price
        if obj and obj.mesto_snapshot:
            return obj.mesto_snapshot
        elif obj and obj.product_price and obj.product_price.product and obj.product_price.product.mesto:
            return obj.product_price.product.mesto
        return 'Место не указано'
    product_mesto.short_description = 'Место'
    
    def product_zacup_price(self, obj):
        # Приоритет: zacup_price_snapshot, fallback к product_price
        if obj and obj.zacup_price_snapshot is not None:
            return obj.zacup_price_snapshot
        elif obj and obj.product_price and obj.product_price.zacup_price is not None:
            return obj.product_price.zacup_price
        return 'Не указано'
    product_zacup_price.short_description = 'Закупочная цена'

    
    class Media:
        js = ('admin/js/vendor/jquery/jquery.min.js', 'my_js/dynamic_orderitem_fields.js',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name_last_name',
        'email',
        'paid',
        'status',
        'phone',
        'region',
        'city',
        'address',
        'postal_code',   
        'get_total_cost',
        'get_total_zakup_cost',
        order_pdf, 
    ]
    
    list_editable = ['paid', 'status']
    readonly_fields = ['get_total_zakup_cost', 'get_total_cost']
    list_filter = ['paid', 'created', 'updated'] 
    inlines = [OrderItemInline]
    search_fields = ['items__article_snapshot', 'items__product_price__product__article_number', 'first_name_last_name', 'email', 'phone', 'city']  # Обновлено: добавлен поиск по article_snapshot
    list_display_links = ['id', 'first_name_last_name'] 

    
    def get_queryset(self, request):
        # Загружаем связанные модели для оптимизации запросов
        queryset = super().get_queryset(request).select_related('delivery_method', 'discount').prefetch_related(
            'items__product_price__product',
            'items__product_price__size',
        )
        return queryset

    def get_delivery_price(self, obj):
        # Проверяем, установлен ли способ доставки
        if obj.delivery_method:
            # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
            return obj.price_delivery if obj.price_delivery is not None else "Не указано"
        return "Не указано"  # Если способ доставки не указан

    get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки
    

    def get_total_zakup_cost(self, obj):
        # Приоритет snapshots для архивных данных, fallback к product_price
        total_cost = sum(
            ((item.zacup_price_snapshot if item.zacup_price_snapshot is not None else (item.product_price.zacup_price if item.product_price and item.product_price.zacup_price is not None else 0)) * item.quantity)
            for item in obj.items.all()
        )
        return total_cost
    get_total_zakup_cost.short_description = 'Общая закупочная стоимость'  # Заголовок для отображения

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(items__article_snapshot__icontains=search_term) |  # Поиск по snapshot
                Q(items__product_price__product__article_number__icontains=search_term) |  # Поиск по связанным
                Q(first_name_last_name__icontains=search_term) | 
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            ).distinct()
        return super().get_search_results(request, queryset, search_term)
    

    change_list_template = "admin/orders/order/change_list.html"  # Укажите свой шаблон

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('top_client/', self.admin_site.admin_view(self.top_client_view), name='top_client'),
        ]
        return custom_urls + urls

    def top_client_view(self, request):
        now = timezone.now()

        # Получаем все заказы с оптимизацией
        orders = self.get_queryset(request).filter(paid=True, email__isnull=False)
        
        # Создаем словарь для хранения информации о клиентах
        client_data = {}

        for order in orders:
            email = order.email
            if not email:  # Пропускаем заказы без email
                continue
            
            if email not in client_data:
                client_data[email] = {
                    'first_name_last_name': order.first_name_last_name,
                    'phone': order.phone,
                    'city': order.city,
                    'total_orders': 0,
                    'total_spent': 0,
                    'last_purchase': order.created,
                }
            
            client_data[email]['total_orders'] += 1
            client_data[email]['total_spent'] += order.get_total_cost()
            client_data[email]['last_purchase'] = max(client_data[email]['last_purchase'], order.created)
        
        top_clients = sorted(client_data.items(), key=lambda x: x[1]['total_spent'], reverse=True)[:100]

        # Рассчитываем средний чек и период
        for email, client in top_clients:
            client['average_check'] = (
                client['total_spent'] / client['total_orders'] 
                if client['total_orders'] > 0 else 0
            )
            client['average_period'] = (
                (now - client['last_purchase']).days // client['total_orders'] 
                if client['total_orders'] > 0 else 0
            )

        return render(request, 'admin/orders/order/top_client.html', {
            'top_clients': top_clients,
        })

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['top_client_url'] = reverse('admin:top_client')
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_title', 'price', 'is_price_custom', 'quantity', 'size_title']  # Обновлено: используем методы для отображения
    change_list_template = "admin/orders/orderitem/change_list.html"  # Укажите свой шаблон

    def product_title(self, obj):
        # Приоритет: product_snapshot, fallback к product_price
        if obj and obj.product_snapshot:
            return obj.product_snapshot
        elif obj and obj.product_price and obj.product_price.product:
            return obj.product_price.product.title
        return 'Нет товара'
    product_title.short_description = 'Товар'

    def size_title(self, obj):
        # Приоритет: size_snapshot, fallback к product_price
        if obj and obj.size_snapshot:
            return obj.size_snapshot
        elif obj and obj.product_price and obj.product_price.size:
            return obj.product_price.size.title
        return 'Размер не указан'
    size_title.short_description = 'Размер'

    def get_queryset(self, request):
        # Загружаем связанные модели для оптимизации запросов
        queryset = super().get_queryset(request)
        return queryset.select_related('product_price__product', 'product_price__size', 'order')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('top_product/', self.admin_site.admin_view(self.top_products_view), name='top_product'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['top_product_url'] = reverse('admin:top_product')
        return super().changelist_view(request, extra_context=extra_context)

    def top_products_view(self, request):
        now = timezone.now()
        period_mapping = {
            '1_month': now - timedelta(days=30),
            '3_months': now - timedelta(days=90),
            '1_year': now - timedelta(days=365),
        }

        # Базовый запрос: фильтруем OrderItem с существующими связями и paid=True
        base_queryset = OrderItem.objects.select_related(
            'order', 'product_price__product'
        ).exclude(
            product_price__isnull=True, 
            product_price__product__isnull=True, 
            order__isnull=True
        ).filter(order__paid=True)  # Добавлено: только оплаченные заказы

        # Отдельные запросы для каждого периода
        top_products_month = (
            base_queryset
            .filter(order__created__gte=period_mapping['1_month'])
            .values(
                product_title=F('product_price__product__title'),
                article_number=F('product_price__product__article_number')
            )
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
        )[:60]

        top_products_three_months = (
            base_queryset
            .filter(order__created__gte=period_mapping['3_months'])
            .values(
                product_title=F('product_price__product__title'),
                article_number=F('product_price__product__article_number')
            )
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
        )[:60]

        top_products_year = (
            base_queryset
            .filter(order__created__gte=period_mapping['1_year'])
            .values(
                product_title=F('product_price__product__title'),
                article_number=F('product_price__product__article_number')
            )
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')
        )[:60]

        return render(request, 'admin/orders/orderitem/top_product.html', {
            'top_products_month': top_products_month,
            'top_products_three_months': top_products_three_months,
            'top_products_year': top_products_year,
        })

@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = [
        'title'
    ]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'discount_value')
