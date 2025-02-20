from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from home.models import Product,Category
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST,product=product)
    print("Данные из формы:", request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,quantity=cd['quantity'],override_quantity=cd['override'],size=cd['size'],)
        
    else:
        # Обработка ошибки: форма не валидна
        print("Форма не валидна:", form.errors)  # Вывод ошибок формы для отладки
        # print(f"Форма валидна: {form.is_valid()}, данные: {cd}")

    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id) 
    # Получаем размер из POST-запроса
    size = request.POST.get('size')  # Убедитесь, что размер передается
    cart.remove(product, size)
    return redirect('cart:cart_detail')


def cart_detail(request):
    categories = Category.objects.all()
    cart = Cart(request)
    get_root_catalog = categories.first().get_absolute_url()
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True, 'size': item['size'],})
    print("Содержимое корзины:", cart.get_cart_items()) 
    return render(request, 'cart/cart_page.html', {
        'cart': cart,
        'categories': categories,
        'get_root_catalog': get_root_catalog
    })