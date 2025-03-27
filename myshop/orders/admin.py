from django.contrib import admin
from .models import Order, OrderItem, DeliveryMethod, Discount
from django.utils.safestring import mark_safe
from django.db.models import Q, Sum
from django.urls import reverse, path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from home.models import ProductPrice




def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id]) 
    return mark_safe(f'<a href="{url}">Чек</a>')
order_pdf.short_description = 'Чеки'



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    fields = ['product_image','product','product_article_number','size','product_mesto','product_zacup_price','quantity', 'price','get_cost',]
    readonly_fields = ['product_image','product_article_number','product_mesto','product_zacup_price','get_cost']

    def get_queryset(self, request):
        # Загружаем связанные модели для оптимизации запросов
        queryset = super().get_queryset(request)
        return queryset.select_related('size','product','order').prefetch_related(
            'product__images',
            # 'product__product_prices',  # Предварительная загрузка цен для продукта
            # 'size__product_size',  # Если есть связанные размеры
        )
    

    def product_article_number(self, obj):
        return obj.product.article_number
    product_article_number.short_description = 'Артикул'

    def product_mesto(self, obj):
        return obj.product.mesto
    product_mesto.short_description = 'Место'


    def product_zacup_price(self, obj):
        product_prices = obj.product.product_prices.get(size=obj.size)
        print(product_prices.zacup_price)
        return product_prices.zacup_price
    product_zacup_price.short_description = 'Закупочная цена'



    def product_image(self, obj):
        # Получаем все изображения заранее
        images = list(obj.product.images.all())
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
    list_display_links=['id','first_name_last_name',]  # Поля для поиска

    
    def get_queryset(self, request):
        # Загружаем связанные модели для оптимизации запросов
        queryset = super().get_queryset(request)

        # Загружаем все цены в словарь для дальнейшего использования
        self.product_prices = {
            (price.product.id, price.size.id): price.zacup_price
            for price in ProductPrice.objects.all().select_related('product', 'size')
        }

        return queryset.select_related('delivery_method', 'discount').prefetch_related(
            'items__product__product_prices', 
            'items__size__product_size'
        )
    

    def get_delivery_price(self, obj):
        # Проверяем, установлен ли способ доставки
        if obj.delivery_method:
            # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
            return obj.price_delivery if obj.price_delivery is not None else "Не указано"
        return "Не указано"  # Если способ доставки не указан

    get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки

    
    # def get_total_zakup_cost(self, obj):
    #     total_cost = 0
    #     for item in obj.items.all():  # Предполагаем, что у вас есть связь с элементами заказа
    #         # Получаем все цены для каждого товара, которые уже загружены
    #         product_prices = {price.size: price for price in item.product.product_prices.all()}
    #         print(product_prices)
    #         total_cost += product_prices.get(item.size).zacup_price * item.quantity  # Умножаем на количество
    #     return total_cost

    # get_total_zakup_cost.short_description = 'Общая закупочная стоимость'  # Заголовок для отображения
    


    def get_total_zakup_cost(self, obj):
        total_cost = 0
        for item in obj.items.all():  # Проходим по всем элементам заказа
            # Получаем цену для данного размера из словаря
            price = self.product_prices.get((item.product.id, item.size.id))

            if price is not None:  # Проверяем, существует ли цена
                total_cost += price * item.quantity  # Умножаем на количество
            else:
                print(f'Цена для размера {item.size} не найдена для продукта {item.product.name}')

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
        print(f"Количество заказов: {orders.count()}")

        # Создаем словарь для хранения информации о клиентах
        client_data = {}

        for order in orders:
            print(f"Заказ ID: {order.id}, Email: {order.email}, Сумма: {order.get_total_cost()}")
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
        if not client_data:
            print("Нет данных о клиентах.")

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



