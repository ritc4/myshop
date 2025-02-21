from cart.cart import Cart
from django.shortcuts import render
from .forms import OrderCreateForm
from .models import OrderItem
from home.models import Category


def order_create(request): 
    categories = Category.objects.all()
    cart = Cart(request)
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
        {'cart': cart, 'form': form,'categories': categories,}
    ) 