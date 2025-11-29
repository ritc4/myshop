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






# import os  # Добавь импорт для работы с путями
# from celery import shared_task
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
# from django.conf import settings
# import weasyprint
# from .models import Order

# @shared_task
# def handle_order_created(order_id, domain):
#     # Получаем объект Order по ID (order_id — int)
#     order = (
#         Order.objects.select_related("delivery_method")
#         .prefetch_related("items__product", "items__size")
#         .get(id=order_id)
#     )

#     # Логика для создания и отправки письма
#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()
    
#     # Строим локальный путь к логотипу (без URL!)
#     # settings.STATIC_ROOT — это путь к статическим файлам, например, /app/static
#     logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')
#     # Проверяем, существует ли файл (опционально, для отладки)
#     if not os.path.exists(logo_path):
#         raise FileNotFoundError(f"Logo not found at {logo_path}")
    
#     html = render_to_string(
#         "orders/order/pdf.html",
#         {
#             "order": order,
#             "total_quantity": total_quantity,
#             "total_items": total_items,
#             "logo_path": logo_path,  # Теперь это локальный путь, не URL
#         },
#     )

#     # Создание PDF
#     pdf = weasyprint.HTML(string=html).write_pdf(
#         stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
#     )
    
#     subject = f"Заказ № {order.id} в интернет-магазине Cozy.su"
    
#     # Отправка письма с PDF как вложением
#     email = EmailMessage(
#         subject=subject,
#         body="Спасибо за ваш заказ! В скором времени мы с вами свяжемся.",
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[order.email],
#     )
    
#     email.attach(f"Ваш Заказ № {order.id}.pdf", pdf, "application/pdf")
#     return email.send()  # Возвращает int (количество отправленных писем)


# # рабочий 
# from celery import shared_task
# from django.core.mail import send_mail
# from .models import Order
# import weasyprint
# from django.conf import settings
# from django.templatetags.static import static
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string


# @shared_task
# def handle_order_created(order_id):
#     order = Order.objects.select_related('delivery_method').prefetch_related('items__product_price__product', 'items__product_price__size').get(id=order_id)

#     # Логика для создания и отправки письма
#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()
#     # Получаем путь к файлу, а не URL
#     logo_path = settings.STATIC_ROOT / 'img/logo.png'

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
#         to=[order.email], bcc=[settings.ADMIN_EMAIL]  # order.email, Используйте email покупателя из заказа и добавить адрес админа
#     )
#     # print(settings.DEFAULT_FROM_EMAIL, order.email)
#     email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
#     return email.send()





# новый 
# import os
# from celery import shared_task
# from django.core.mail import send_mail, EmailMessage
# from django.template.loader import render_to_string
# from django.conf import settings
# from .models import Order
# import weasyprint


# # Функция для поиска файла в статических директориях
# def get_static_file_path(filename):
#     """
#     Ищет файл сначала в STATICFILES_DIRS (для dev-режима), затем в STATIC_ROOT (для prod).
#     Возвращает полный путь к файлу или None, если не найден.
#     """
#     # Проверим STATICFILES_DIRS
#     for dir_path in getattr(settings, 'STATICFILES_DIRS', []):
#         file_path = os.path.join(dir_path, filename)
#         if os.path.exists(file_path):
#             return file_path
#     # Проверим STATIC_ROOT
#     file_path = os.path.join(settings.STATIC_ROOT, filename)
#     if os.path.exists(file_path):
#         return file_path
#     return None


# @shared_task
# def handle_order_created(order_id):
#     order = Order.objects.select_related('delivery_method').prefetch_related('items__product_price__product', 'items__product_price__size').get(id=order_id)


#     # Логика для создания и отправки письма
#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()
    
#     # Найдем путь к логотипу (для использования в HTML как <img src="file://...">)
#     logo_path = get_static_file_path('img/logo.png')
    
#     html = render_to_string(
#         'orders/order/pdf.html', {
#             'order': order,
#             'total_quantity': total_quantity,
#             'total_items': total_items,
#             'logo_path': logo_path,  # Передаём путь в шаблон (шаблон должен использовать его как <img src="file://{{ logo_path }}">)
#         }
#     )

#     # Создание PDF
#     css_path = get_static_file_path('css/pdf.css')
#     stylesheets = [weasyprint.CSS(css_path)] if css_path else []  # Если CSS не найден, PDF без стилей
    
#     pdf = weasyprint.HTML(string=html).write_pdf(stylesheets=stylesheets)
    
#     subject = f'Заказ № {order.id} в интернет-магазине Cozy.su'
    
#     # Отправка письма с PDF как вложением
#     email = EmailMessage(
#         subject=subject,
#         body='Спасибо за ваш заказ! В скором времени мы с вами свяжемся.',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[order.email],
#         bcc=[settings.ADMIN_EMAIL]  # Добавляем BCC для админа
#     )
#     # print(settings.DEFAULT_FROM_EMAIL, order.email)  # Для дебага
#     email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
#     return email.send()


# новый 2
from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from weasyprint import HTML, CSS  # Обновлён импорт для современного WeasyPrint
from django.conf import settings
from django.templatetags.static import static
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging
import time
from threading import Thread
from io import BytesIO

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # Повторы: до 3 раз с задержкой 60 сек
def handle_order_created(self, order_id):
    try:
        # Получение заказа с оптимизированными запросами
        order = Order.objects.select_related('delivery_method').prefetch_related(
            'items__product_price__product', 'items__product_price__size'
        ).get(id=order_id)
        
        # Логика для данных в шаблоне
        total_quantity = sum(item.quantity for item in order.items.all())
        total_items = order.items.count()
        logo_path = settings.STATIC_ROOT / 'img/logo.png'
        
        # Подготовка контекста для шаблона
        context = {
            'order': order,
            'total_quantity': total_quantity,
            'total_items': total_items,
            'logo_path': logo_path,
        }
        
        # Функция для генерации PDF в отдельном треде (с целью предотвратить зависание)
        html_pdf_content = None
        pdf_content = BytesIO()
        
        def generate_pdf_in_thread():
            nonlocal html_pdf_content
            html_pdf_content = render_to_string('orders/order/pdf.html', context)
            HTML(string=html_pdf_content, base_url=settings.STATIC_URL).write_pdf(
                target=pdf_content,
                stylesheets=[CSS(settings.STATIC_ROOT / 'css/pdf.css')]
            )
        
        # Начало измерения времени
        start_time = time.time()
        
        # Запуск генерации в треде с таймаутом 30 секунд (настройте по необходимости)
        thread = Thread(target=generate_pdf_in_thread)
        thread.start()
        thread.join(timeout=30)  # Таймаут: если превысил 30 сек, считаем неудачей
        
        if thread.is_alive():
            logger.warning(f"PDF generation for order {order_id} timed out, retrying...")
            raise self.retry(countdown=60, exc=Exception("PDF generation timeout"))
        
        logger.info(f"PDF generation for order {order_id} took {time.time() - start_time:.2f} seconds")
        
        # Получение PDF из BytesIO
        pdf = pdf_content.getvalue()
        
        # Формирование и отправка email
        subject = f'Заказ № {order.id} в интернет-магазине Cozy.su'
        email = EmailMessage(
            subject=subject,
            body='Спасибо за ваш заказ! В скором времени мы с вами свяжемся.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
            bcc=[settings.ADMIN_EMAIL]
        )
        email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
        
        # Отправка письма
        result = email.send()
        logger.info(f"Email for order {order_id} sent successfully.")
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_order_created for order {order_id}: {str(e)}")
        # Повтор задачи при ошибке
        raise self.retry()