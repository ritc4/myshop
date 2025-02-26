from cart.cart import Cart
from django.shortcuts import render,redirect
from .forms import OrderCreateForm
from .models import OrderItem
from home.models import Category,Politica_firm,Uslovie_firm


def order_create(request): 
    categories = Category.objects.all()
    cart = Cart(request)
    get_root_catalog = categories.first().get_absolute_url()
    politica = Politica_firm.objects.first()
    uslovia = Uslovie_firm.objects.first()

    # Проверка на наличие товаров в корзине
    if not cart or not any(item['quantity'] > 0 for item in cart):
        return redirect(get_root_catalog)  # Перенаправляем на страницу товаров
    

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order, 
                    product=item['product'], 
                    price=item['price'], 
                    quantity=item['quantity'],
                    size=item['size'],  # Передаем размер
            )
            # очистить корзину
            cart.clear()
            return render(
                request, 'orders/order/checkout_finish_page.html', {'order': order,'categories': categories,}
            )
    else:
        form = OrderCreateForm()
    return render(
        request,
        'orders/order/checkout_page.html',
        {'cart': cart, 'form': form,'categories': categories,'politica':politica,'uslovia':uslovia}
    ) 