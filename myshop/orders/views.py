from cart.cart import Cart
from django.shortcuts import get_object_or_404,render,redirect
from .forms import OrderCreateForm
from .models import OrderItem,Order
from home.models import Category,Politica_firm,Uslovie_firm
from django.template.loader import render_to_string
from django.http import HttpResponse 
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint 
from django.contrib.staticfiles import finders
from django.conf import settings
from django.templatetags.static import static
from .signals import order_created_signal  # Импортируйте ваш сигнал


def order_create(request): 
    categories = Category.objects.all()
    cart = Cart(request)
    get_root_catalog = categories.first().get_absolute_url()
    politica = Politica_firm.objects.first()
    uslovia = Uslovie_firm.objects.first()

    # Проверка на наличие товаров в корзине
    if not cart or not any(item['quantity'] > 0 for item in cart):
        return redirect(get_root_catalog)  # Перенаправляем на страницу товаров
    
    # Создание хлебных крошек
    breadcrumbs = [
        {'name': 'Оформление заказа', 'slug': '/orders/'}  # Текущая страница без ссылки
        ]
    
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)  # Передаем пользователя в форму
        if form.is_valid():
            order = form.save(commit=False)  # Создаем объект заказа, но не сохраняем его еще
            order.user = request.user  # Если у вас есть связь с пользователем
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order, 
                    product=item['product'], 
                    price=item['price'], 
                    quantity=item['quantity'],
                    size=item['size'],  # Передаем размер
                )
            # Очистить корзину
            cart.clear()
            # Отправить сигнал после успешного создания заказа
            order_created_signal.send(sender=OrderItem, order_id=order.id, request=request)
            return render(
                request, 'orders/order/checkout_finish_page.html', {'order': order, 'categories': categories, 'breadcrumbs': breadcrumbs}
            )
    else:
        form = OrderCreateForm(user=request.user)  # Передаем пользователя в форму

    return render(
        request,
        'orders/order/checkout_page.html',
        {'cart': cart, 'form': form, 'categories': categories, 'politica': politica, 'uslovia': uslovia, 'breadcrumbs': breadcrumbs}
    )




@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

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




