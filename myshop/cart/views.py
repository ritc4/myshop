# from django.shortcuts import get_object_or_404, redirect, render
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
# from django.template.loader import render_to_string
# from home.models import Product, Category, ProductPrice
# from .cart import Cart
# from .forms import CartAddProductForm
# from .templatetags.custom_filters import russian_pluralize
# import logging

# logger = logging.getLogger(__name__)

# @require_POST 
# def cart_add(request, product_id):
#     try:
#         cart = Cart(request)
#         product = get_object_or_404(Product, id=product_id)

#         sizes = ProductPrice.objects.filter(product_id=product_id).select_related('size')
#         size_price_map = [(str(size.size.title), size.price) for size in sizes]

#         form = CartAddProductForm(request.POST, product=product, sizes=size_price_map)

#         if form.is_valid():
#             cd = form.cleaned_data
#             quantity = cd['quantity']
#             if quantity < 1:
#                 quantity = 1  # Устанавливаем минимум, чтобы избежать ошибок
#             size = cd.get('size')
#             cart.add(product=product, quantity=quantity, override_quantity=cd['override'], size=size)

#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 item = cart.get_item(str(product.id), size)
#                 total_items = len(cart)
#                 pluralized_text = russian_pluralize(total_items, "товар,товара,товаров") if total_items > 0 else ""
#                 is_empty = total_items == 0

#                 # Обновлённый элемент для оптимизации UI
#                 updated_items = [{
#                     'product_id': product.id,
#                     'size': size,
#                     'quantity': item['quantity'],
#                     'total_price': item['total_price']
#                 }]

#                 # Генерация HTML (упрощённая, без request для избежания ошибок)
#                 html_cart_page = render_to_string('cart/cart_table_body.html', {
#                     'cart': cart,
#                     'is_cart_empty': is_empty,
#                 })
#                 html_checkout_page = render_to_string('orders/order/checkout_cart_tbody.html', {
#                     'cart': cart,
#                 })

#                 # Для мобильных карточек (новый шаблон)
#                 html_checkout_cards = render_to_string('orders/order/checkout_cart_cards.html', {
#                     'cart': cart,
#                 })

#                 html_offcanvas = render_to_string('cart/cart_offcanvas.html', {
#                     'cart': cart,
#                     'is_cart_empty': is_empty,
#                     'categories': Category.objects.all(),
#                 })

#                 return JsonResponse({
#                     'success': True,
#                     'item_total_price': str(item['total_price']),
#                     'cart_total_price': str(cart.get_total_price()),
#                     'cart_item_count': total_items,
#                     'pluralized_text': pluralized_text,
#                     'quantity': item['quantity'],
#                     'updated_items': updated_items,
#                     'is_empty': is_empty,
#                     'html_cart_page': html_cart_page,
#                     'html_checkout_page': html_checkout_page,
#                     'html_offcanvas': html_offcanvas,
#                     'html_checkout_cards': html_checkout_cards,
#                 })
#             else:
#                 referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
#                 return redirect(referer)
#         else:
#             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'error': str(form.errors)})
#             referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
#             return redirect(referer)
#     except Exception as e:
#         logger.error(f"Error in cart_add: {e}", exc_info=True)
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({'success': False, 'error': 'Internal server error'})
#         return redirect('cart:cart_detail')

# @require_POST
# def cart_remove(request, product_id):
#     try:
#         cart = Cart(request)
#         product = get_object_or_404(Product, id=product_id)
#         size = request.POST.get('size')
#         cart.remove(product, size)

#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             total_items = len(cart)
#             pluralized_text = russian_pluralize(total_items, "товар,товара,товаров") if total_items > 0 else ""
#             is_empty = total_items == 0

#             # Для удалённого элемента указываем quantity=0, чтобы JS удалил строку
#             updated_items = [{
#                 'product_id': product.id,
#                 'size': size,
#                 'quantity': 0,
#                 'total_price': '0'  # Не актуально, но для consistency
#             }]

#             html_cart_page = render_to_string('cart/cart_table_body.html', {
#                 'cart': cart,
#                 'is_cart_empty': is_empty,
#             })
#             html_checkout_page = render_to_string('orders/order/checkout_cart_tbody.html', {
#                 'cart': cart,
#             })
#             # Для мобильных карточек (новый шаблон)
#             html_checkout_cards = render_to_string('orders/order/checkout_cart_cards.html', {
#                 'cart': cart,
#             })
#             html_offcanvas = render_to_string('cart/cart_offcanvas.html', {
#                 'cart': cart,
#                 'is_cart_empty': is_empty,
#                 'categories': Category.objects.all(),
#             })

#             return JsonResponse({
#                 'success': True,
#                 'cart_total_price': str(cart.get_total_price()),
#                 'cart_item_count': total_items,
#                 'pluralized_text': pluralized_text,
#                 'updated_items': updated_items,
#                 'is_empty': is_empty,
#                 'html_cart_page': html_cart_page,
#                 'html_checkout_page': html_checkout_page,
#                 'html_offcanvas': html_offcanvas,
#                 'html_checkout_cards': html_checkout_cards,
#             })
#         else:
#             referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
#             return redirect(referer)
#     except Exception as e:
#         logger.error(f"Error in cart_remove: {e}", exc_info=True)
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({'success': False, 'error': 'Internal server error'})
#         return redirect('cart:cart_detail')

# def cart_detail(request):
#     cart = Cart(request)
#     categories = Category.objects.all()
#     is_cart_empty = len(cart) == 0
    
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('partial') == 'offcanvas':
#         try:
#             html = render_to_string('cart/cart_offcanvas.html', {
#                 'cart': cart,
#                 'is_cart_empty': is_cart_empty,
#                 'categories': categories,
#             })
#             return JsonResponse({'html': html})
#         except Exception as e:
#             logger.error(f"Error in cart_detail offcanvas: {e}", exc_info=True)
#             return JsonResponse({'error': 'Internal server error'})
    
#     return render(request, 'cart/cart_page.html', {
#         'cart': cart,
#         'is_cart_empty': is_cart_empty,
#         'categories': categories,
#     })





from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.template.loader import render_to_string
from home.models import Product, Category, ProductPrice
from .cart import Cart
from .forms import CartAddProductForm
from .templatetags.custom_filters import russian_pluralize
import logging

logger = logging.getLogger(__name__)

@require_POST 
def cart_add(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)

        sizes = ProductPrice.objects.filter(product_id=product_id).select_related('size')
        size_price_map = [(str(size.size.title), size.price) for size in sizes]

        form = CartAddProductForm(request.POST, product=product, sizes=size_price_map)

        if form.is_valid():
            cd = form.cleaned_data
            quantity = cd['quantity']
            if quantity < 1:
                quantity = 1
            size = cd.get('size')
            cart.add(product=product, quantity=quantity, override_quantity=cd['override'], size=size)

            # Добавлено: итерируем для очистки и сбора removed_items
            list(cart)
            removed_items = cart.get_removed_items()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                item = cart.get_item(str(product.id), size)
                total_items = len(cart)
                pluralized_text = russian_pluralize(total_items, "товар,товара,товаров") if total_items > 0 else ""
                is_empty = total_items == 0

                updated_items = [{
                    'product_id': product.id,
                    'size': size,
                    'quantity': item['quantity'],
                    'total_price': item['total_price']
                }]

                html_cart_page = render_to_string('cart/cart_table_body.html', {
                    'cart': cart,
                    'is_cart_empty': is_empty,
                })
                html_checkout_page = render_to_string('orders/order/checkout_cart_tbody.html', {
                    'cart': cart,
                })
                html_checkout_cards = render_to_string('orders/order/checkout_cart_cards.html', {
                    'cart': cart,
                })
                # Теперь removed_items передаётся корректно
                html_offcanvas = render_to_string('cart/cart_offcanvas.html', {
                    'cart': cart,
                    'is_cart_empty': is_empty,
                    'categories': Category.objects.all(),
                    'removed_items': removed_items,
                })

                return JsonResponse({
                    'success': True,
                    'item_total_price': str(item['total_price']),
                    'cart_total_price': str(cart.get_total_price()),
                    'cart_item_count': total_items,
                    'pluralized_text': pluralized_text,
                    'quantity': item['quantity'],
                    'updated_items': updated_items,
                    'is_empty': is_empty,
                    'html_cart_page': html_cart_page,
                    'html_checkout_page': html_checkout_page,
                    'html_offcanvas': html_offcanvas,
                    'html_checkout_cards': html_checkout_cards,
                    'removed_items': removed_items,
                })
            else:
                referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
                return redirect(referer)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(form.errors)})
            referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
            return redirect(referer)
    except Exception as e:
        logger.error(f"Error in cart_add: {e}", exc_info=True)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Internal server error'})
        return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        size = request.POST.get('size')
        cart.remove(product, size)

        # Добавлено: итерируем для очистки и сбора removed_items
        list(cart)
        removed_items = cart.get_removed_items()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            total_items = len(cart)
            pluralized_text = russian_pluralize(total_items, "товар,товара,товаров") if total_items > 0 else ""
            is_empty = total_items == 0

            updated_items = [{
                'product_id': product.id,
                'size': size,
                'quantity': 0,
                'total_price': '0'
            }]

            html_cart_page = render_to_string('cart/cart_table_body.html', {
                'cart': cart,
                'is_cart_empty': is_empty,
            })
            html_checkout_page = render_to_string('orders/order/checkout_cart_tbody.html', {
                'cart': cart,
            })
            html_checkout_cards = render_to_string('orders/order/checkout_cart_cards.html', {
                'cart': cart,
            })
            # Теперь removed_items передаётся корректно
            html_offcanvas = render_to_string('cart/cart_offcanvas.html', {
                'cart': cart,
                'is_cart_empty': is_empty,
                'categories': Category.objects.all(),
                'removed_items': removed_items,
            })

            return JsonResponse({
                'success': True,
                'cart_total_price': str(cart.get_total_price()),
                'cart_item_count': total_items,
                'pluralized_text': pluralized_text,
                'updated_items': updated_items,
                'is_empty': is_empty,
                'html_cart_page': html_cart_page,
                'html_checkout_page': html_checkout_page,
                'html_offcanvas': html_offcanvas,
                'html_checkout_cards': html_checkout_cards,
                'removed_items': removed_items,
            })
        else:
            referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
            return redirect(referer)
    except Exception as e:
        logger.error(f"Error in cart_remove: {e}", exc_info=True)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Internal server error'})
        return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    # Итерируем по корзине заранее для очистки и сбора removed_items
    list(cart)  # Вызывает __iter__, удаляет несуществующие товары и заполняет removed_items
    removed_items = cart.get_removed_items()  # Получаем и очищаем список
    
    categories = Category.objects.all()
    is_cart_empty = len(cart) == 0
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('partial') == 'offcanvas':
        try:
            html = render_to_string('cart/cart_offcanvas.html', {
                'cart': cart,
                'is_cart_empty': is_cart_empty,
                'categories': categories,
                'removed_items': removed_items,
            })
            return JsonResponse({'html': html})
        except Exception as e:
            logger.error(f"Error in cart_detail offcanvas: {e}", exc_info=True)
            return JsonResponse({'error': 'Internal server error'})
    
    return render(request, 'cart/cart_page.html', {
        'cart': cart,
        'is_cart_empty': is_cart_empty,
        'categories': categories,
        'removed_items': removed_items,  # Добавлено для уведомлений в шаблоне
    })
