from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from home.models import Product,Category,ProductPrice
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    sizes = ProductPrice.objects.filter(product_id=product_id).select_related('size')
    size_price_map = [(str(size.size.title), size.price) for size in sizes]

    form = CartAddProductForm(request.POST, product=product, sizes=size_price_map)

    if form.is_valid():
        cd = form.cleaned_data
        size = cd.get('size')
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'], size=size)
    else:
        print("Форма не валидна:", form.errors)

    referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
    return redirect(referer)


# def cart_add(request):
#     cart = Cart(request)

#     # Получаем уникальные продукты (первые 500)
#     products = Product.objects.all()[:500]

#     for product in products:
#         # Получаем связанные размеры и цены для продукта
#         sizes = ProductPrice.objects.filter(product=product).select_related('size')

#         if sizes.exists():
#             # Берем первый размер и его цену
#             first_size = sizes.first()
#             size_title = str(first_size.size.title)
#             price = first_size.price  # Цена не используется в добавлении, но можно сохранить для дальнейшего использования

#             # Добавляем продукт в корзину с первым размером
#             cart.add(product=product, quantity=1, override_quantity=False, size=size_title)

#     referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
#     return redirect(referer)


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id) 
    # Получаем размер из POST-запроса
    size = request.POST.get('size')  # Убедитесь, что размер передается
    cart.remove(product, size)

    # Получаем URL страницы, с которой был запрос
    referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
    return redirect(referer)


def cart_detail(request):
    categories = Category.objects.all()
    cart = Cart(request)
    # Проверка наличия категорий
    if categories.exists():
        get_root_catalog = categories.first().get_absolute_url()
    else:
        get_root_catalog = '#'  # Или можно установить пустую строку или другую логику
    # Проверка на наличие товаров в корзине
    is_cart_empty = not cart or not any(item['quantity'] > 0 for item in cart)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True, 'size': item['size'],})
        
    # Создание хлебных крошек
    breadcrumbs = [
        {'name': 'Корзина', 'slug': '/cart/'}  # Текущая страница без ссылки
        ]
    
    print("Содержимое корзины:", cart.get_cart_items()) 
    return render(request, 'cart/cart_page.html', {
        'cart': cart,
        'categories': categories,
        'get_root_catalog': get_root_catalog, 'is_cart_empty': is_cart_empty,'breadcrumbs': breadcrumbs,  # Добавляем хлебные крошки в контекст
    })

