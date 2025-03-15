from django.contrib import admin
from .models import Order, OrderItem,DeliveryMethod,Discount
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.urls import reverse
from django.db.models import Sum, Count,Max,F,DecimalField
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta








def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id]) 
    return mark_safe(f'<a href="{url}">Чек</a>')
order_pdf.short_description = 'Чеки'



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    fields = ['product_image','product','product_article_number','size','product_mesto','product_zacup_price','quantity', 'price','get_cost',]  # Добавьте поле product_image
    readonly_fields = ['product_image','product_article_number','product_mesto','product_zacup_price','get_cost']  # Убедитесь, что это поле только для чтения


    
    def get_cost(self, obj):  # Добавляем obj как второй аргумент
        return obj.get_cost() if obj else 0  # Проверяем, что obj не равен None
    get_cost.short_description = 'Стоимость'  # Заголовок столбца
    
    
    def product_article_number(self, obj):
        return obj.product_article_number()  # Вызов метода product_image из модели
    product_article_number.short_description = 'Артикул'
    
    def product_image(self, obj):
        return obj.product_image()  # Вызов метода product_image из модели
    product_image.short_description = 'Фото'
    
    def product_mesto(self, obj):
        mesto = obj.product_mesto()  # Вызов метода product_mesto из модели
        return mesto if mesto else 'Не указано'  # Возврат значения или 'Не указано'

    product_mesto.short_description = 'Место'
    
    def product_zacup_price(self, obj):
        return obj.product_zacup_price()  # Вызов метода product_image из модели  
    product_zacup_price.short_description = 'Закупочная цена'

    
 
 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'id',
        'first_name_last_name',
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

    def get_delivery_price(self, obj):
        # Проверяем, установлен ли способ доставки
        if obj.delivery_method:
            # Если цена доставки указана, возвращаем её, иначе возвращаем "Не указано"
            return obj.price_delivery if obj.price_delivery is not None else "Не указано"
        return "Не указано"  # Если способ доставки не указан

    get_delivery_price.short_description = 'Цена доставки'  # Заголовок колонки

    
    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Общая стоимость'


    def get_total_zakup_cost(self, obj):
        return obj.get_total_zakup_cost()
    get_total_zakup_cost.short_description = 'Общая закупочная стоимость'


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
    
    

    # def top_client_view(self, request):
    #     now = timezone.now()
        
    #     # Получаем топ клиентов с необходимыми аннотациями
    #     top_clients = (
            
    #         Order.objects.values('email')
    #         .annotate(
    #             first_name_last_name=Max('first_name_last_name'),  # Берем максимальное значение ФИО
    #             phone=Max('phone'),  # Берем максимальное значение телефона
    #             city=Max('city'),  # Берем максимальное значение города
    #             total_orders=Count('id'),  # Количество заказов
    #             total_spent=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField()),  # Общая сумма по заказам
    #             last_purchase=Max('created')  # Дата последнего заказа
    #         )
    #         .filter(total_orders__gt=0)  # Убедитесь, что у клиентов есть заказы
    #         .order_by('-total_spent')[:100]  # Сортируем по убыванию и берем топ-60
    #     )
        
    #     for order in Order.objects.all():
    #         print(f"Заказ ID: {order.id}, Email: {order.email}, Сумма: {order.get_total_cost()}")
    #     # Рассчитываем средний чек и период
    #     for client in top_clients:
    #         print(client)
    #         client['average_check'] = (
    #             client['total_spent'] / client['total_orders'] 
    #             if client['total_orders'] > 0 else 0
    #         )
    #         client['average_period'] = (
    #             (now - client['last_purchase']).days // client['total_orders'] 
    #             if client['total_orders'] > 0 else 0
    #         )
    
    #     return render(request, 'admin/orders/order/top_client.html', {
    #         'top_clients': top_clients,
    #     })
    

    def top_client_view(self, request):
        now = timezone.now()

        # Получаем все заказы
        orders = Order.objects.all()
        print(f"Количество заказов: {orders.count()}")

        # Создаем словарь для хранения информации о клиентах
        client_data = {}

        for order in orders:
            print(f"Заказ ID: {order.id}, Email: {order.email}, Сумма: {order.get_total_cost()}")
            email = order.email
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
    list_display =[
        'order','product','price','quantity','size',
        ]

    change_list_template = "admin/orders/orderitem/change_list.html"  # Укажите свой шаблон

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
    

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['top_product_url'] = reverse('admin:top_product')
        return super().changelist_view(request, extra_context=extra_context)



@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display =[
        'title'
        ]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'discount_value')



