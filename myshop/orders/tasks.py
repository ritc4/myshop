# from io import BytesIO
# # # from celery import shared_task
# import weasyprint
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string 
# from orders.models import Order
# from django.shortcuts import get_object_or_404
# from django.contrib.staticfiles import finders
# from django.conf import settings
# from django.templatetags.static import static
# # from .signals import order_created_signal  # Импортируйте ваш сигнал

# # @shared_task
# # def payment_completed(order_id):
# #     order = get_object_or_404(Order, id=order_id)
    
# #     # Предполагаем, что у вас есть методы для получения нужных значений
# #     total_quantity = sum(item.quantity for item in order.items.all())
# #     total_items = order.items.count()

# #     # Передаем дополнительные данные в контекст
# #     html = render_to_string(
# #         'orders/order/pdf.html', {
# #             'order': order,
# #             'total_quantity': total_quantity,
# #             'total_items': total_items
# #         }
# #     )
    
# #     print(order.items.all())

# #     # Отправка письма с HTML содержимым
# #     subject = f'Заказ № {order.id} - Подробности'
# #     email = EmailMessage(
# #         subject,
# #         html,  # Используем сгенерированный HTML как тело письма
# #         'ritc4@rambler.ru',  # Замените на реальный адрес отправителя
# #         ['ritc4@rambler.ru'],  # Замените на реальный адрес получателя
# #     )
    
# #     email.content_subtype = 'html'  # Указываем, что содержимое - HTML

# #     try:
# #         # Отправляем электронное письмо
# #         email.send()
# #     except Exception as e:
# #         print(f"Ошибка при отправке письма: {e}")





# from celery import shared_task
# from django.core.mail import send_mail
# from .models import Order
# import weasyprint
# from django.conf import settings
# from django.templatetags.static import static
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string


# @shared_task
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
#     return email.send()



from celery import shared_task  # <-- Должен быть импорт из celery (не myshop.celery)
from django.core.mail import send_mail
from .models import Order
import weasyprint
from django.conf import settings
from django.templatetags.static import static
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

@shared_task
def handle_order_created(order_id, absolute_url):  # <-- Изменили параметр: order_id (int) вместо order (object)
    order = Order.objects.select_related('delivery_method').prefetch_related('items__product', 'items__size').get(id=order_id)  # <-- Используем order_id для get(id=...)

    # Логика для создания и отправки письма
    total_quantity = sum(item.quantity for item in order.items.all())
    total_items = order.items.count()
    logo_path = absolute_url + static('img/logo.png')  # <-- absolute_url — строка, переданная из views.py

    html = render_to_string(
        'orders/order/pdf.html', {
            'order': order,
            'total_quantity': total_quantity,
            'total_items': total_items,
            'logo_path': logo_path,
        }
    )

    # Создание PDF
    pdf = weasyprint.HTML(string=html).write_pdf(
        stylesheets=[
            weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')
        ]
    )
    subject = f'Заказ № {order.id} в интернет-магазине Cozy.su'
    # Отправка письма с PDF как вложением

    email = EmailMessage(
        subject=subject,
        body='Спасибо за ваш заказ! В скором времени мы с вами свяжемся.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],  # order.email — email покупателя; добавь админа, если нужно: to=[order.email, 'admin@example.com']
    )
    print(settings.DEFAULT_FROM_EMAIL, order.email)
    email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
    return email.send()
