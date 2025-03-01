from django.dispatch import Signal, receiver
from django.shortcuts import get_object_or_404
from .models import Order  # Импортируйте вашу модель заказа
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import weasyprint
from django.templatetags.static import static

# Определите сигнал
order_created_signal = Signal()  # Уберите providing_args

@receiver(order_created_signal)
def handle_order_created(request, order_id, **kwargs):
    order = get_object_or_404(Order, id=order_id)

    # Логика для создания и отправки письма
    total_quantity = sum(item.quantity for item in order.items.all())
    total_items = order.items.count()
    logo_path = request.build_absolute_uri(static('img/logo.png'))

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
    subject = f'Заказ № {order.id} в интернет магазине Cozy.su'
    # Отправка письма с PDF как вложением

    email = EmailMessage(
        subject=subject,
        body='Спасибо за ваш заказ! В скором времени мы с вами свяжемся.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],  # Используйте email покупателя из заказа
    )
    print(order.email)
    email.attach(f'Ваш Заказ № {order.id}.pdf', pdf, 'application/pdf')
    email.send()