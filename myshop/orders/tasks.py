from io import BytesIO
# # from celery import shared_task
import weasyprint
from django.core.mail import EmailMessage
from django.template.loader import render_to_string 
from orders.models import Order
from django.shortcuts import get_object_or_404
from django.contrib.staticfiles import finders
from django.conf import settings
from django.templatetags.static import static
# from .signals import order_created_signal  # Импортируйте ваш сигнал

# @shared_task
# def payment_completed(order_id):
#     order = get_object_or_404(Order, id=order_id)
    
#     # Предполагаем, что у вас есть методы для получения нужных значений
#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()

#     # Передаем дополнительные данные в контекст
#     html = render_to_string(
#         'orders/order/pdf.html', {
#             'order': order,
#             'total_quantity': total_quantity,
#             'total_items': total_items
#         }
#     )
    
#     print(order.items.all())

#     # Отправка письма с HTML содержимым
#     subject = f'Заказ № {order.id} - Подробности'
#     email = EmailMessage(
#         subject,
#         html,  # Используем сгенерированный HTML как тело письма
#         'ritc4@rambler.ru',  # Замените на реальный адрес отправителя
#         ['ritc4@rambler.ru'],  # Замените на реальный адрес получателя
#     )
    
#     email.content_subtype = 'html'  # Указываем, что содержимое - HTML

#     try:
#         # Отправляем электронное письмо
#         email.send()
#     except Exception as e:
#         print(f"Ошибка при отправке письма: {e}")


