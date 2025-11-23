from django.contrib import admin
from .models import Order, OrderItem, DeliveryMethod, Discount
from django.utils.safestring import mark_safe
from django.db.models import Q, Sum
from django.urls import reverse, path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from home.models import ProductPrice,Size,Product



def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id]) 
    return mark_safe(f'<a href="{url}">Чек</a>')
order_pdf.short_description = 'Чеки'



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    show_change_link = True
    raw_id_fields = ['product']
    extra = 1  # Количество пустых форм для добавления новых элементов
    fields = ['product_image','product','product_article_number','size','product_mesto','product_zacup_price','quantity', 'price','get_cost']
    readonly_fields = ['product_image','product_article_number','product_mesto','product_zacup_price','get_cost']


    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('product','size').prefetch_related(
            'product__images',
            'product__product_prices',
        )

        return queryset
    


    def product_article_number(self, obj):
        return obj.product.article_number if obj.product and obj.product.article_number else 'Артикул не указан'
    product_article_number.short_description = 'Артикул'

    def product_mesto(self, obj):
        return obj.product.mesto if obj.product and obj.product.mesto else 'Место не указано'
    product_mesto.short_description = 'Место'

    def product_image(self, obj):
        # Получаем все изображения заранее
        images = obj.product.images.all()  # Используем предзагруженные изображения
        if images:
            first_image = images[0]
            return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
        else:
            return 'Нет фото'
    product_image.short_description = 'Фото товара'



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
    
    list_editable = ['paid','status',]
    readonly_fields = ['get_total_zakup_cost','get_total_cost']
    list_filter = ['paid', 'created', 'updated'] 
    inlines = [OrderItemInline]
    search_fields = ['items__product__article_number','first_name_last_name', 'email', 'phone','city']
    list_display_links=['id','first_name_last_name',] 

    
    def get_queryset(self, request):
        # Загружаем связанные модели для оптимизации запросов
        queryset = super().get_queryset(request).select_related('delivery_method', 'discount').prefetch_related(
            'items__product',
            'items__size',
        )

        # Загружаем все цены в словарь для дальнейшего использования
        self.product_prices = {
            (price.product.id, price.size.id): price.zacup_price
            for price in ProductPrice.objects.all().select_related('product', 'size')
        }

        return queryset


    def get_delivery_price(self, obj):
        # Проверяем, установлен ли способ доставки
        if obj.delivery_method:
            # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
            return obj.price_delivery if obj.price_delivery is not None else "Не указано"
        return "Не указано"  # Если способ доставки не указан

    get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки
    

    def get_total_zakup_cost(self, obj):
        total_cost = 0
        for item in obj.items.all():
            price = self.product_prices.get((item.product.id, item.size.id))
            if price is not None:
                total_cost += price * item.quantity
        return total_cost
    get_total_zakup_cost.short_description = 'Общая закупочная стоимость'  # Заголовок для отображения



    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(items__product__article_number__icontains=search_term) | 
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
        orders = self.get_queryset(request)  # Используем get_queryset для загрузки заказов
        

        # Создаем словарь для хранения информации о клиентах
        client_data = {}

        for order in orders:
            # print(f"Заказ ID: {order.id}, Email: {order.email}, Сумма: {order.get_total_cost()}")
            email = order.email

            # Проверяем, существует ли email в словаре
            if email not in client_data:
                client_data[email] = {
                    'first_name_last_name': order.first_name_last_name,
                    'phone': order.phone,
                    'city': order.city,
                    'total_orders': 0,
                    'total_spent': 0,
                    'last_purchase': order.created,
                }

            # Обновляем информацию о клиенте
            client_data[email]['total_orders'] += 1
            client_data[email]['total_spent'] += order.get_total_cost()  # Используем метод get_total_cost
            client_data[email]['last_purchase'] = max(client_data[email]['last_purchase'], order.created)

        # Проверяем, есть ли собранные данные
        # if not client_data:
            # print("Нет данных о клиентах.")

        # Преобразуем данные в список и сортируем по total_spent
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
    list_display = ['order', 'product', 'price', 'quantity', 'size']
    change_list_template = "admin/orders/orderitem/change_list.html"  # Укажите свой шаблон

    def get_queryset(self, request):
        # Загружаем связанные модели для оптимизации запросов
        queryset = super().get_queryset(request)
        return queryset.select_related('product','size','order')
    
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

        # Определяем временные рамки для различных периодов
        period_mapping = {
            '1_month': now - timedelta(days=30),
            '3_months': now - timedelta(days=90),
            '1_year': now - timedelta(days=365),
        }

        # Получаем все заказы за последний год и группируем по продуктам
        all_orders = (
            OrderItem.objects.filter(order__created__gte=period_mapping['1_year'])
            .select_related('product')  # Используем select_related для оптимизации
            .values('product__title', 'product__article_number')  # Используем article_number
            .annotate(total_quantity=Sum('quantity'))  # Суммируем количество
        )

        # Группируем данные по периодам
        top_products_month = (
            all_orders.filter(order__created__gte=period_mapping['1_month'])
            .order_by('-total_quantity')[:60]
        )

        top_products_three_months = (
            all_orders.filter(order__created__gte=period_mapping['3_months'])
            .order_by('-total_quantity')[:60]
        )

        top_products_year = (
            all_orders.order_by('-total_quantity')[:60]
        )

        return render(request, 'admin/orders/orderitem/top_product.html', {
            'top_products_month': top_products_month,
            'top_products_three_months': top_products_three_months,
            'top_products_year': top_products_year,
        })



@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display =[
        'title'
        ]
    

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'discount_value')










# from django.contrib import admin
# from .models import Order, OrderItem, DeliveryMethod, Discount
# from django.utils.safestring import mark_safe
# from django.db.models import Q, Sum
# from django.urls import reverse, path
# from django.shortcuts import render
# from django.utils import timezone
# from datetime import timedelta
# from home.models import ProductPrice,Size,Product
# from django import forms
# from django.db.models import Subquery, OuterRef, F
# from django.contrib.admin.widgets import ForeignKeyRawIdWidget


# def order_pdf(obj):
#     url = reverse('orders:admin_order_pdf', args=[obj.id]) 
#     return mark_safe(f'<a href="{url}">Чек</a>')
# order_pdf.short_description = 'Чеки'



# # class OrderItemForm(forms.ModelForm):
# #     class Meta:
# #         model = OrderItem
# #         fields = ['product', 'size']

# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)

# #         # Устанавливаем начальный queryset для поля size
# #         self.fields['size'].queryset = Size.objects.all()
# #         self.fields['product'].queryset = Product.objects.all()

# #         # Если есть данные о продукте, фильтруем размеры
# #         product_id = self.data.get('product') or (self.instance.product.id if self.instance.pk else None)
# #         if product_id:
# #             try:
# #                 # Преобразуем product_id в целое число
# #                 product_id = int(product_id)
# #                 # Фильтруем размеры по выбранному продукту
# #                 self.fields['size'].queryset = Size.objects.filter(product_size__product__id=product_id)
# #             except (ValueError, TypeError):
# #                 # Если возникла ошибка, оставляем все размеры
# #                 self.fields['size'].queryset = Size.objects.all()

# #     def clean(self):
# #         cleaned_data = super().clean()
# #         product = cleaned_data.get('product')

# #         # Если продукт выбран, фильтруем размеры по этому продукту
# #         if product:
# #             self.fields['size'].queryset = Size.objects.filter(product_size__product=product)

# #         return cleaned_data


# # class OrderItemInline(admin.TabularInline):
# #     model = OrderItem
# #     show_change_link = True
# #     form = OrderItemForm
# #     raw_id_fields = ['product']
# #     extra = 1  # Количество пустых форм для добавления новых элементов
# #     fields = ['product_image','product','product_article_number','size','product_mesto','product_zacup_price','quantity', 'price','get_cost']
# #     readonly_fields = ['product_image','product_article_number','product_mesto','product_zacup_price','get_cost']


# #     def get_queryset(self, request):
# #         queryset = super().get_queryset(request).select_related('product','size').prefetch_related(
# #             'product__images',
# #             'product__product_prices',
# #         )

# #         return queryset
    


# #     def product_article_number(self, obj):
# #         return obj.product.article_number if obj.product and obj.product.article_number else 'Артикул не указан'
# #     product_article_number.short_description = 'Артикул'

# #     def product_mesto(self, obj):
# #         return obj.product.mesto if obj.product and obj.product.mesto else 'Место не указано'
# #     product_mesto.short_description = 'Место'

# #     def product_image(self, obj):
# #         # Получаем все изображения заранее
# #         images = obj.product.images.all()  # Используем предзагруженные изображения
# #         if images:
# #             first_image = images[0]
# #             return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
# #         else:
# #             return 'Нет фото'
# #     product_image.short_description = 'Фото товара'


# class CachedForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
#     _label_cache = {}

#     def label_for_value(self, obj):
#         # Возвращаем строковое представление объекта (например, obj.__str__())
#         return str(obj)

#     def label_and_url_for_value(self, value):
#         if value in self._label_cache:
#             return self._label_cache[value]
#         # Fallback к оригиналу, если не в кэше (хотя мы preload)
#         obj = self.rel.model._default_manager.using(self.db).get(**{self.rel.get_related_field().name: value})
#         label = self.label_for_value(obj)  # Теперь это работает
#         # Конструируем URL вручную, поскольку url_for_result может быть недоступен
#         url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
#         self._label_cache[value] = (label, url)
#         return label, url


# class OrderItemForm(forms.ModelForm):
#     class Meta:
#         model = OrderItem
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Устанавливаем queryset для size как все размеры (для новых объектов)
#         self.fields['size'].queryset = Size.objects.all()

#     def clean(self):
#         cleaned_data = super().clean()
#         product = cleaned_data.get('product')
#         size = cleaned_data.get('size')
        
#         # Если продукт и размер выбраны, проверяем, что размер доступен для продукта
#         if product and size:
#             if not product.product_prices.filter(size=size).exists():
#                 raise forms.ValidationError("Выбранный размер недоступен для этого продукта.")
        
#         return cleaned_data

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     show_change_link = True
#     form = OrderItemForm
#     raw_id_fields = ['product']
#     extra = 1
#     fields = ['product_image', 'product', 'product_article_number', 'size', 'product_mesto', 'product_zacup_price', 'quantity', 'price', 'get_cost']
#     readonly_fields = ['product_image', 'product_article_number', 'product_mesto', 'product_zacup_price', 'get_cost']

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'product':
#             kwargs['widget'] = CachedForeignKeyRawIdWidget(db_field.remote_field, self.admin_site)
#             return db_field.formfield(**kwargs)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         queryset = queryset.select_related('product', 'size')
#         queryset = queryset.prefetch_related('product__product_prices__size', 'product__images')
#         queryset = queryset.annotate(
#             zacup_price=Subquery(
#                 ProductPrice.objects.filter(
#                     product=OuterRef('product'),
#                     size=OuterRef('size')
#                 ).values('zacup_price')[:1]
#             ),
#             article_number=F('product__article_number'),
#             mesto=F('product__mesto'),
#             total_cost=F('quantity') * F('price'),
#         )
        
#         product_ids = set(queryset.values_list('product_id', flat=True))
#         if product_ids:
#             # Предварительная загрузка продуктов в кэш DB
#             products = list(Product.objects.filter(id__in=product_ids))
#             # Заполнение кэша виджета метками и URL
#             for p in products:
#                 url = reverse(f'admin:{p._meta.app_label}_{p._meta.model_name}_change', args=[p.pk])
#                 CachedForeignKeyRawIdWidget._label_cache[p.pk] = (str(p), url)
        
#         size_ids = set(queryset.values_list('size_id', flat=True))
#         if size_ids:
#             list(Size.objects.filter(id__in=size_ids))  # Загружаем sizes в кэш
        
#         return queryset

#     def product_article_number(self, obj):
#         return obj.article_number if obj.article_number else 'Артикул не указан'
#     product_article_number.short_description = 'Артикул'

#     def product_mesto(self, obj):
#         return obj.mesto if obj.mesto else 'Место не указано'
#     product_mesto.short_description = 'Место'

#     def product_image(self, obj):
#         images = obj.product.images.all()
#         if images:
#             first_image = images[0]
#             return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
#         else:
#             return 'Нет фото'
#     product_image.short_description = 'Фото товара'

#     def product_zacup_price(self, obj):
#         return obj.zacup_price if obj.zacup_price is not None else 'Нет цены'
#     product_zacup_price.short_description = 'Закупочная цена'

#     def get_cost(self, obj):
#         return obj.total_cost
#     get_cost.short_description = 'Общая стоимость'
 



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
#          order_pdf, 
#         ]
    
#     list_editable = ['paid','status',]
#     readonly_fields = ['get_total_zakup_cost','get_total_cost']
#     list_filter = ['paid', 'created', 'updated'] 
#     inlines = [OrderItemInline]
#     search_fields = ['items__product__article_number','first_name_last_name', 'email', 'phone','city']
#     list_display_links=['id','first_name_last_name',] 

    
#     def get_queryset(self, request):
#         # Загружаем связанные модели для оптимизации запросов
#         queryset = super().get_queryset(request).select_related('delivery_method', 'discount').prefetch_related(
#             'items__product',
#             'items__size',
#         )

#         # Загружаем все цены в словарь для дальнейшего использования
#         self.product_prices = {
#             (price.product.id, price.size.id): price.zacup_price
#             for price in ProductPrice.objects.all().select_related('product', 'size')
#         }

#         return queryset


#     def get_delivery_price(self, obj):
#         # Проверяем, установлен ли способ доставки
#         if obj.delivery_method:
#             # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
#             return obj.price_delivery if obj.price_delivery is not None else "Не указано"
#         return "Не указано"  # Если способ доставки не указан

#     get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки
    

#     def get_total_zakup_cost(self, obj):
#         total_cost = 0
#         for item in obj.items.all():
#             price = self.product_prices.get((item.product.id, item.size.id))
#             if price is not None:
#                 total_cost += price * item.quantity
#         return total_cost
#     get_total_zakup_cost.short_description = 'Общая закупочная стоимость'  # Заголовок для отображения



#     def get_search_results(self, request, queryset, search_term):
#         if search_term:
#             queryset = queryset.filter(
#                 Q(items__product__article_number__icontains=search_term) | 
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

#         # Проверяем, есть ли собранные данные
#         # if not client_data:
#             # print("Нет данных о клиентах.")

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
#     list_display = ['order', 'product', 'price', 'quantity', 'size']
#     change_list_template = "admin/orders/orderitem/change_list.html"  # Укажите свой шаблон

#     def get_queryset(self, request):
#         # Загружаем связанные модели для оптимизации запросов
#         queryset = super().get_queryset(request)
#         return queryset.select_related('product','size','order')
    
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
#             .select_related('product')  # Используем select_related для оптимизации
#             .values('product__title', 'product__article_number')  # Используем article_number
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
#     list_display =[
#         'title'
#         ]
    

# @admin.register(Discount)
# class DiscountAdmin(admin.ModelAdmin):
#     list_display = ('discount_type', 'discount_value')








# '''Рабочий'''
# from django.contrib import admin
# from .models import Order, OrderItem, DeliveryMethod, Discount
# from django.utils.safestring import mark_safe
# from django.db.models import Q, Sum
# from django.urls import reverse, path
# from django.shortcuts import render
# from django.utils import timezone
# from datetime import timedelta
# from home.models import ProductPrice, Size, Product
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.core.exceptions import ValidationError  # Добавлено для валидации в clean()


# def order_pdf(obj):
#     url = reverse('orders:admin_order_pdf', args=[obj.id]) 
#     return mark_safe(f'<a href="{url}">Чек</a>')
# order_pdf.short_description = 'Чеки'


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     show_change_link = True
#     raw_id_fields = ['product']
#     extra = 1  # Количество пустых форм для добавления новых элементов
#     fields = ['product_image', 'product', 'product_article_number', 'size', 'product_mesto', 'product_zacup_price', 'quantity', 'price', 'get_cost']
#     readonly_fields = ['product_image', 'product_article_number', 'product_mesto', 'product_zacup_price', 'get_cost']

#     def get_formset(self, request, obj=None, **kwargs):
#         formset = super().get_formset(request, obj, **kwargs)
        
#         class OrderItemForm(formset.form):
#             def __init__(self, *args, **kwargs):
#                 super().__init__(*args, **kwargs)
#                 # Убрано ограничение queryset для size — теперь все размеры доступны,
#                 # JS динамически добавит только релевантные опции.
#                 # Валидация будет в clean().
            
#             def clean(self):
#                 cleaned_data = super().clean()
#                 product = cleaned_data.get('product')
#                 size = cleaned_data.get('size')
#                 if product and size:
#                     # Проверяем, существует ли связь через ProductPrice
#                     if not ProductPrice.objects.filter(product=product, size=size).exists():
#                         raise ValidationError("Выбранный размер недоступен для этого товара.")
#                 return cleaned_data
        
#         formset.form = OrderItemForm
#         return formset

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request).select_related('product', 'size').prefetch_related(
#             'product__images',
#             'product__product_prices',
#         )
#         return queryset

#     class Media:
#         js = ('admin/js/vendor/jquery/jquery.min.js', 'my_js/dynamic_orderitem_fields.js')

#     def product_article_number(self, obj):
#         return obj.product.article_number if obj.product and obj.product.article_number else 'Артикул не указан'
#     product_article_number.short_description = 'Артикул'

#     def product_mesto(self, obj):
#         return obj.product.mesto if obj.product and obj.product.mesto else 'Место не указано'
#     product_mesto.short_description = 'Место'

#     def product_image(self, obj):
#         # Получаем все изображения заранее
#         images = obj.product.images.all()  # Используем предзагруженные изображения
#         if images:
#             first_image = images[0]
#             return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
#         else:
#             return 'Нет фото'
#     product_image.short_description = 'Фото товара'


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
#     search_fields = ['items__product__article_number', 'first_name_last_name', 'email', 'phone', 'city']
#     list_display_links = ['id', 'first_name_last_name']

#     def get_queryset(self, request):
#         # Загружаем связанные модели для оптимизации запросов
#         queryset = super().get_queryset(request).select_related('delivery_method', 'discount').prefetch_related(
#             'items__product',
#             'items__size',
#         )

#         # Загружаем все цены в словарь для дальнейшего использования
#         self.product_prices = {
#             (price.product.id, price.size.id): price.zacup_price
#             for price in ProductPrice.objects.all().select_related('product', 'size')
#         }

#         return queryset

#     def get_delivery_price(self, obj):
#         # Проверяем, установлен ли способ доставки
#         if obj.delivery_method:
#             # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
#             return obj.price_delivery if obj.price_delivery is not None else "Не указано"
#         return "Не указано"  # Если способ доставки не указан

#     get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки

#     def get_total_zakup_cost(self, obj):
#         total_cost = 0
#         for item in obj.items.all():
#             price = self.product_prices.get((item.product.id, item.size.id))
#             if price is not None:
#                 total_cost += price * item.quantity
#         return total_cost
#     get_total_zakup_cost.short_description = 'Общая закупочная стоимость'  # Заголовок для отображения

#     def get_search_results(self, request, queryset, search_term):
#         if search_term:
#             queryset = queryset.filter(
#                 Q(items__product__article_number__icontains=search_term) | 
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
#             path('get_sizes/<int:product_id>/', self.admin_site.admin_view(self.get_sizes), name='get_sizes'),
#             path('get_prices/<int:product_id>/<int:size_id>/', self.admin_site.admin_view(self.get_prices), name='get_prices'),
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

#         # Проверяем, есть ли собранные данные
#         # if not client_data:
#             # print("Нет данных о клиентах.")

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

#     def get_sizes(self, request, product_id):
#         """Возвращает размеры для товара в формате JSON: {'sizes': [{'id': id, 'title': title}, ...]}"""
#         if request.method == 'GET':
#             try:
#                 # Проверяем существование продукта
#                 get_object_or_404(Product, id=product_id)
#                 # Фильтруем размеры по ProductPrice (исправлено: используем правильный related_name 'product_size')
#                 sizes = Size.objects.filter(product_size__product_id=product_id).distinct()
#                 sizes_data = [{'id': size.id, 'title': str(size.title)} for size in sizes]
#                 return JsonResponse({'sizes': sizes_data})
#             except Exception as e:
#                 return JsonResponse({'error': str(e)}, status=400)
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

#     def get_prices(self, request, product_id, size_id):
#         """Возвращает цены для товара и размера в формате JSON: {'zacup_price': value, 'price': value}"""
#         if request.method == 'GET':
#             try:
#                 price_obj = ProductPrice.objects.filter(product_id=product_id, size_id=size_id).first()
#                 if price_obj:
#                     return JsonResponse({
#                         'zacup_price': str(price_obj.zacup_price),  # Преобразуем в строку для JS
#                         'price': str(price_obj.price)
#                     })
#                 return JsonResponse({'error': 'Цена не найдена'}, status=404)
#             except Exception as e:
#                 return JsonResponse({'error': str(e)}, status=400)
#         return JsonResponse({'error': 'Method not allowed'}, status=405)


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ['order', 'product', 'price', 'quantity', 'size']
#     change_list_template = "admin/orders/orderitem/change_list.html"  # Укажите свой шаблон

#     def get_queryset(self, request):
#         # Загружаем связанные модели для оптимизации запросов
#         queryset = super().get_queryset(request)
#         return queryset.select_related('product', 'size', 'order')
    
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
#             .select_related('product')  # Используем select_related для оптимизации
#             .values('product__title', 'product__article_number')  # Используем article_number
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







# новый 
# from django.contrib import admin
# from django import forms
# from django.contrib.admin.widgets import ForeignKeyRawIdWidget
# from django.urls import reverse
# from django.db.models import Subquery, OuterRef, F, Q, Sum
# from .models import Order, OrderItem, DeliveryMethod, Discount
# from django.utils.safestring import mark_safe
# from django.urls import reverse, path
# from django.shortcuts import render
# from django.utils import timezone
# from datetime import timedelta
# from home.models import ProductPrice, Size, Product
# from django.core.cache import cache  # Добавлено для кэширования choices


# def order_pdf(obj):
#     url = reverse('orders:admin_order_pdf', args=[obj.id]) 
#     return mark_safe(f'<a href="{url}">Чек</a>')
# order_pdf.short_description = 'Чеки'


# # Кэширование choices для Size (чтобы избежать повторных запросов при рендере select в inline)
# def get_cached_size_choices():
#     key = 'size_choices'
#     choices = cache.get(key)
#     if choices is None:
#         choices = list(Size.objects.values_list('id', 'title'))
#         cache.set(key, choices, 3600)  # Кэш на 1 час
#     return choices


# # Кэширование choices для Product (для полноты, хотя raw_id не рендерит select)
# def get_cached_product_choices():
#     key = 'product_choices'
#     choices = cache.get(key)
#     if choices is None:
#         choices = list(Product.objects.values_list('id', 'title'))
#         cache.set(key, choices, 3600)  # Кэш на 1 час
#     return choices


# class CachedForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
#     _label_cache = {}

#     def label_for_value(self, obj):
#         return str(obj)

#     def label_and_url_for_value(self, value):
#         if value in self._label_cache:
#             return self._label_cache[value]
#         obj = self.rel.model._default_manager.using(self.db).get(**{self.rel.get_related_field().name: value})
#         label = self.label_for_value(obj)
#         url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
#         self._label_cache[value] = (label, url)
#         return label, url


# class OrderItemForm(forms.ModelForm):
#     class Meta:
#         model = OrderItem
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Кэшируем choices для size, чтобы избежать повторных запросов при рендере select
#         self.fields['size'].choices = get_cached_size_choices()
#         self.fields['size'].queryset = Size.objects.all()  # Оставляем для валидации
        
#         # Кэшируем choices для product (для полноты)
#         self.fields['product'].choices = get_cached_product_choices()
#         self.fields['product'].queryset = Product.objects.all()


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     show_change_link = True
#     form = OrderItemForm
#     raw_id_fields = ['product']
#     extra = 1
#     fields = ['product_image', 'product', 'product_article_number', 'size', 'product_mesto', 'product_zacup_price', 'quantity', 'price', 'get_cost']
#     readonly_fields = ['product_image', 'product_article_number', 'product_mesto', 'product_zacup_price', 'get_cost']

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         queryset = queryset.select_related('product', 'size')
#         # Убрал prefetch_related('product__product_prices__size') — аннотации покрывают Subquery
#         queryset = queryset.prefetch_related('product__images')
#         queryset = queryset.annotate(
#             zacup_price=Subquery(
#                 ProductPrice.objects.filter(
#                     product=OuterRef('product'),
#                     size=OuterRef('size')
#                 ).values('zacup_price')[:1]
#             ),
#             article_number=F('product__article_number'),
#             mesto=F('product__mesto'),
#             total_cost=F('quantity') * F('price'),
#         )
        
#         product_ids = set(queryset.values_list('product_id', flat=True))
#         if product_ids:
#             products = list(Product.objects.filter(id__in=product_ids))
#             for p in products:
#                 url = reverse(f'admin:{p._meta.app_label}_{p._meta.model_name}_change', args=[p.pk])
#                 CachedForeignKeyRawIdWidget._label_cache[p.pk] = (str(p), url)
        
#         size_ids = set(queryset.values_list('size_id', flat=True))
#         if size_ids:
#             list(Size.objects.filter(id__in=size_ids))  # Загружаем существующие sizes в кэш
        
#         return queryset

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'product':
#             kwargs['widget'] = CachedForeignKeyRawIdWidget(db_field.remote_field, self.admin_site)
#             return db_field.formfield(**kwargs)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     def product_zacup_price(self, obj):
#         return obj.zacup_price if obj.zacup_price is not None else 'Не указано'
#     product_zacup_price.short_description = 'Закупочная цена'

#     def product_article_number(self, obj):
#         return obj.article_number if obj.article_number else 'Артикул не указан'
#     product_article_number.short_description = 'Артикул'

#     def product_mesto(self, obj):
#         return obj.mesto if obj.mesto else 'Место не указано'
#     product_mesto.short_description = 'Место'

#     def product_image(self, obj):
#         images = obj.product.images.all()
#         if images:
#             first_image = images[0]
#             return mark_safe(f"<img src='{first_image.image.url}' width='50'>")
#         else:
#             return 'Нет фото'
#     product_image.short_description = 'Фото товара'

#     def get_cost(self, obj):
#         return obj.total_cost if obj.total_cost else 0
#     get_cost.short_description = 'Стоимость позиции'


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
#          order_pdf, 
#         ]
    
#     list_editable = ['paid','status',]
#     readonly_fields = ['get_total_zakup_cost','get_total_cost']
#     list_filter = ['paid', 'created', 'updated'] 
#     inlines = [OrderItemInline]
#     search_fields = ['items__product__article_number','first_name_last_name', 'email', 'phone','city']
#     list_display_links=['id','first_name_last_name',] 

#     class Media:
#         js = ('admin/js/vendor/jquery/jquery.min.js', 'my_js/dynamic_orderitem_fields.js')
    
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request).select_related('delivery_method', 'discount').prefetch_related(
#             'items__product',
#             'items__size',
#         )

#         self.product_prices = {
#             (price.product.id, price.size.id): price.zacup_price
#             for price in ProductPrice.objects.all().select_related('product', 'size')
#         }

#         return queryset

#     def get_delivery_price(self, obj):
#         if obj.delivery_method:
#             return obj.price_delivery if obj.price_delivery is not None else "Не указано"
#         return "Не указано"

#     get_delivery_price.short_description = 'Цена доставки'
    
#     def get_total_zakup_cost(self, obj):
#         total_cost = 0
#         for item in obj.items.all():
#             price = self.product_prices.get((item.product.id, item.size.id))
#             if price is not None:
#                 total_cost += price * item.quantity
#         return total_cost
#     get_total_zakup_cost.short_description = 'Общая закупочная стоимость'

#     def get_search_results(self, request, queryset, search_term):
#         if search_term:
#             queryset = queryset.filter(
#                 Q(items__product__article_number__icontains=search_term) | 
#                 Q(first_name_last_name__icontains=search_term) | 
#                 Q(email__icontains=search_term) |
#                 Q(phone__icontains=search_term)
#             ).distinct()
#         return super().get_search_results(request, queryset, search_term)
    
#     change_list_template = "admin/orders/order/change_list.html"

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('top_client/', self.admin_site.admin_view(self.top_client_view), name='top_client'),
#         ]
#         return custom_urls + urls

#     def top_client_view(self, request):
#         now = timezone.now()

#         orders = self.get_queryset(request)
        
#         client_data = {}

#         for order in orders:
#             email = order.email

#             if email not in client_data:
#                 client_data[email] = {
#                     'first_name_last_name': order.first_name_last_name,
#                     'phone': order.phone,
#                     'city': order.city,
#                     'total_orders': 0,
#                     'total_spent': 0,
#                     'last_purchase': order.created,
#                 }

#             client_data[email]['total_orders'] += 1
#             client_data[email]['total_spent'] += order.get_total_cost()
#             client_data[email]['last_purchase'] = max(client_data[email]['last_purchase'], order.created)

#         top_clients = sorted(client_data.items(), key=lambda x: x[1]['total_spent'], reverse=True)[:100]

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
#     list_display = ['order', 'product', 'price', 'quantity', 'size']
#     change_list_template = "admin/orders/orderitem/change_list.html"

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related('product','size','order')
    
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

#         period_mapping = {
#             '1_month': now - timedelta(days=30),
#             '3_months': now - timedelta(days=90),
#             '1_year': now - timedelta(days=365),
#         }

#         all_orders = (
#             OrderItem.objects.filter(order__created__gte=period_mapping['1_year'])
#             .select_related('product')
#             .values('product__title', 'product__article_number')
#             .annotate(total_quantity=Sum('quantity'))
#         )

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

#         return render(request, 'admin/orders/order/top_product.html', {
#             'top_products_month': top_products_month,
#             'top_products_three_months': top_products_three_months,
#             'top_products_year': top_products_year,
#         })


# @admin.register(DeliveryMethod)
# class DeliveryMethodAdmin(admin.ModelAdmin):
#     list_display=[
#         'title'
#         ]
    

# @admin.register(Discount)
# class DiscountAdmin(admin.ModelAdmin):
#     list_display = ('discount_type', 'discount_value')

