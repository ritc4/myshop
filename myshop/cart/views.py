from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from home.models import Product,Category
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,quantity=cd['quantity'],
        override_quantity=cd['override'])

    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id) 
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    categories = Category.objects.all()
    cart = Cart(request)
    return render(request, 'cart/cart_page.html', {'cart': cart,'categories':categories})