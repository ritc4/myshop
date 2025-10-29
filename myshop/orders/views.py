from cart.cart import Cart
from django.shortcuts import get_object_or_404,render,redirect
from .forms import OrderCreateForm
from .models import OrderItem,Order
from home.models import Category,Politica_firm,Uslovie_firm,Size,Product
from django.template.loader import render_to_string
from django.http import HttpResponse 
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint 
from django.conf import settings
from django.templatetags.static import static
from django.core.mail import EmailMessage
from .tasks import handle_order_created


# def handle_order_created(order, request):
#     order = Order.objects.select_related('delivery_method').prefetch_related('items__product', 'items__size').get(id=order.id)

#     # Логика для создания и отправки письма
#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()
#     logo_path = request.build_absolute_uri(static('img/logo.png'))

#     html = render_to_string(
#         'orders/order/pdf.html', {
#             'order': order,
#             'total_quantity': total_quantity,
#             'total_items': total_items,
#             'logo_path': logo_path,
#         }
#     )

#     # Создание PDF
#     pdf = weasyprint.HTML(string=html).write_pdf(
#         stylesheets=[
#             weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')
#         ]
#     )
#     subject = f'Заказ № {order.id} в интернет-магазине Cozy.su'
#     # Отправка письма с PDF как вложением

#     email = EmailMessage(
#         subject=subject,
#         body='Спасибо за ваш заказ! В скором времени мы с вами свяжемся.',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[order.email],  # order.email, Используйте email покупателя из заказа и добавить адрес админа
#     )
#     print(settings.DEFAULT_FROM_EMAIL, order.email)
#     email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
#     email.send()




def order_create(request): 
    categories = Category.objects.all()
    cart = Cart(request)
    # get_root_catalog = categories.first().get_absolute_url()
    # Добавляем проверку: если категорий нет, устанавливаем fallback на главную страницу
    first_category = categories.first()
    if first_category:
        get_root_catalog = first_category.get_absolute_url()
    else:
        get_root_catalog = '/'  # Или reverse('home:index') если у тебя есть именованный URL для главной
    politica = Politica_firm.objects.first()
    uslovia = Uslovie_firm.objects.first()

    # Проверка на наличие товаров в корзине
    if not cart or not any(item['quantity'] > 0 for item in cart):
        return redirect(get_root_catalog)

    breadcrumbs = [{'name': 'Оформление заказа', 'slug': '/orders/'}] 
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            order_items = []

            # Собираем идентификаторы продуктов и размеры
            product_ids = [int(item['product_id']) for item in cart]
            size_titles = [item['size'] for item in cart]

            # Получаем все продукты и размеры за один запрос
            products = Product.objects.filter(id__in=product_ids).select_related('category')
            sizes = Size.objects.filter(title__in=size_titles)

            # Создаем словари для быстрого доступа
            product_dict = {product.id: product for product in products}
            size_dict = {size.title: size for size in sizes}

            for item in cart:
                # Получаем экземпляры продукта и размера
                product_instance = product_dict.get(int(item['product_id']))
                size_instance = size_dict.get(item['size'])

                if product_instance and size_instance:
                    order_item = OrderItem(
                        order=order, 
                        product=product_instance, 
                        price=item['price'], 
                        quantity=item['quantity'],
                        size=size_instance,
                    )
                    order_items.append(order_item)
                else:
                    # Обработка случаев, когда продукт или размер не найдены
                    print(f"Product or size not found for item: {item}")

            # Сохраняем все элементы заказа за один раз
            OrderItem.objects.bulk_create(order_items)

            # Очистить корзину
            cart.clear()

            # Вызов функции обработки события
            handle_order_created.delay(order.id, request.build_absolute_uri('/'))

            return render(request, 'orders/order/checkout_finish_page.html')
    else:
        form = OrderCreateForm(user=request.user)
    

    # Добавлено: передача title в контекст
    title = breadcrumbs[0]['name'] if breadcrumbs else 'Оформление заказа'

    return render(
        request,
        'orders/order/checkout_page.html',
        {'cart': cart, 'form': form, 'categories': categories, 'politica': politica, 'uslovia': uslovia, 'breadcrumbs': breadcrumbs,'title': title}
    )





@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order.objects.select_related('delivery_method').prefetch_related('items__product','items'), id=order_id)

    # Подсчет общего количества товаров и позиций
    total_quantity = sum(item.quantity for item in order.items.all())  # Общее количество товаров
    total_items = order.items.count()  # Общее количество позиций
    logo_path = request.build_absolute_uri(static('img/logo.png'))

    html = render_to_string(
        'orders/order/pdf.html', {
            'order': order,
            'total_quantity': total_quantity,
            'total_items': total_items,
             'logo_path':logo_path,
        }
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'filename=order_{order.id}.pdf' 
    )
    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[
            weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')
        ]
    ) 
    return response




