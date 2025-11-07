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



from celery import shared_task
from django.core.mail import send_mail
from .models import Order
import weasyprint
from django.conf import settings
from django.templatetags.static import static
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def handle_order_created(order_id):
    order = Order.objects.select_related('delivery_method').prefetch_related('items__product', 'items__size').get(id=order_id)

    # Логика для создания и отправки письма
    total_quantity = sum(item.quantity for item in order.items.all())
    total_items = order.items.count()
    # Получаем путь к файлу, а не URL
    logo_path = settings.STATIC_ROOT / 'img/logo.png'   # static('img/logo.png')

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
        to=[order.email], bcc=[settings.ADMIN_EMAIL]  # order.email, Используйте email покупателя из заказа и добавить адрес админа
    )
    print(settings.DEFAULT_FROM_EMAIL, order.email)
    email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
    return email.send()




#для логирования и поиска ошибок
# from celery import shared_task
# from django.core.mail import send_mail
# from .models import Order
# import weasyprint
# from django.conf import settings
# from django.templatetags.static import static
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
# import logging

# logger = logging.getLogger(__name__)


# @shared_task
# def handle_order_created(order_id):
#     print(f"Начало обработки заказа {order_id}")
#     logger.info(f"Начало обработки заказа {order_id}")
#     try:
#         order = Order.objects.select_related('delivery_method').prefetch_related('items__product', 'items__size').get(
#             id=order_id)
#         print(f"Заказ {order_id} получен")
#         logger.info(f"Заказ {order_id} получен")
#     except Order.DoesNotExist:
#         print(f"Заказ {order_id} не найден")
#         logger.error(f"Заказ {order_id} не найден")
#         return False  # Или raise, в зависимости от вашей логики

#     # Логика для создания и отправки письма
#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()
#     # Получаем путь к файлу, а не URL
#     logo_path = settings.STATIC_ROOT / 'img/logo.png'  # static('img/logo.png')
#     print(f"Путь к логотипу: {logo_path}")
#     logger.info(f"Путь к логотипу: {logo_path}")

#     print("Рендеринг HTML")
#     logger.info("Рендеринг HTML")
#     try:
#         html = render_to_string(
#             'orders/order/pdf.html', {
#                 'order': order,
#                 'total_quantity': total_quantity,
#                 'total_items': total_items,
#                 'logo_path': logo_path,
#             }
#         )
#         print("HTML отрендерен")
#         logger.info("HTML отрендерен")

#     except Exception as e:
#         print(f"Ошибка при рендеринге HTML: {e}")
#         logger.exception(f"Ошибка при рендеринге HTML: {e}")
#         return False

#     # Создание PDF
#     print("Создание PDF")
#     logger.info("Создание PDF")
#     try:
#         pdf = weasyprint.HTML(string=html).write_pdf(
#             stylesheets=[
#                 weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')
#             ]
#         )
#         print("PDF создан")
#         logger.info("PDF создан")
#     except Exception as e:
#         print(f"Ошибка при создании PDF: {e}")
#         logger.exception(f"Ошибка при создании PDF: {e}")
#         return False

#     subject = f'Заказ № {order.id} в интернет-магазине Cozy.su'
#     # Отправка письма с PDF как вложением

#     print("Подготовка EmailMessage")
#     logger.info("Подготовка EmailMessage")
#     try:
#         email = EmailMessage(
#             subject=subject,
#             body='Спасибо за ваш заказ! В скором времени мы с вами свяжемся.',
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[order.email],  # order.email, Используйте email покупателя из заказа и добавить адрес админа
#         )
#         print(f"from_email: {settings.DEFAULT_FROM_EMAIL}, to: {order.email}")
#         logger.info(f"from_email: {settings.DEFAULT_FROM_EMAIL}, to: {order.email}")
#         email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
#         print("EmailMessage подготовлен")
#         logger.info("EmailMessage подготовлен")
#     except Exception as e:
#         print(f"Ошибка при подготовке EmailMessage: {e}")
#         logger.exception(f"Ошибка при подготовке EmailMessage: {e}")
#         return False

#     # Отправка письма. Важно обернуть в try-except, чтобы отловить ошибку отправки.
#     try:
#         print("Отправка Email")
#         logger.info("Отправка Email")
#         result = email.send()
#         print(f"Результат отправки Email: {result}")
#         logger.info(f"Результат отправки Email: {result}")
#         return result  # Возвращаем результат отправки (обычно 1 при успехе)
#     except Exception as e:
#         print(f"Ошибка при отправке Email: {e}")
#         logger.exception(f"Ошибка при отправке Email: {e}")
#         return False

#     print(f"Завершение обработки заказа {order_id}")
#     logger.info(f"Завершение обработки заказа {order_id}")
