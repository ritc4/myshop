# from cart.cart import Cart
# from django.shortcuts import get_object_or_404, render, redirect
# from .forms import OrderCreateForm
# from .models import OrderItem, Order
# from home.models import Category, Politica_firm, Uslovie_firm, Size, Product
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from django.contrib.admin.views.decorators import staff_member_required
# import weasyprint
# from django.conf import settings
# from django.templatetags.static import static
# from .tasks import handle_order_created


# def order_create(request):
#     categories = Category.objects.all()
#     cart = Cart(request)
#     # get_root_catalog = categories.first().get_absolute_url()
#     # Добавляем проверку: если категорий нет, устанавливаем fallback на главную страницу
#     first_category = categories.first()
#     if first_category:
#         get_root_catalog = first_category.get_absolute_url()
#     else:
#         get_root_catalog = "/"  # Или reverse('home:index') если у тебя есть именованный URL для главной
#     politica = Politica_firm.objects.first()
#     uslovia = Uslovie_firm.objects.first()

#     # Проверка на наличие товаров в корзине
#     if not cart or not any(item["quantity"] > 0 for item in cart):
#         return redirect(get_root_catalog)

#     breadcrumbs = [{"name": "Оформление заказа", "slug": "/orders/"}]

#     if request.method == "POST":
#         form = OrderCreateForm(request.POST, user=request.user)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.user = request.user
#             order.save()

#             order_items = []

#             # Собираем идентификаторы продуктов и размеры
#             product_ids = [int(item["product_id"]) for item in cart]
#             size_titles = [item["size"] for item in cart]

#             # Получаем все продукты и размеры за один запрос
#             products = Product.objects.filter(id__in=product_ids).select_related(
#                 "category"
#             )
#             sizes = Size.objects.filter(title__in=size_titles)

#             # Создаем словари для быстрого доступа
#             product_dict = {product.id: product for product in products}
#             size_dict = {size.title: size for size in sizes}

#             for item in cart:
#                 # Получаем экземпляры продукта и размера
#                 product_instance = product_dict.get(int(item["product_id"]))
#                 size_instance = size_dict.get(item["size"])

#                 if product_instance and size_instance:
#                     order_item = OrderItem(
#                         order=order,
#                         product=product_instance,
#                         price=item["price"],
#                         quantity=item["quantity"],
#                         size=size_instance,
#                     )
#                     order_items.append(order_item)
#                 else:
#                     # Обработка случаев, когда продукт или размер не найдены
#                     print(f"Product or size not found for item: {item}")

#             # Сохраняем все элементы заказа за один раз
#             OrderItem.objects.bulk_create(order_items)

#             # Очистить корзину
#             cart.clear()

#             # Вызов функции обработки события
#             handle_order_created.delay(order.id)

#             return render(request, "orders/order/checkout_finish_page.html")
#     else:
#         form = OrderCreateForm(user=request.user)

#     # Добавлено: передача title в контекст
#     title = breadcrumbs[0]["name"] if breadcrumbs else "Оформление заказа"

#     return render(
#         request,
#         "orders/order/checkout_page.html",
#         {
#             "cart": cart,
#             "form": form,
#             "categories": categories,
#             "politica": politica,
#             "uslovia": uslovia,
#             "breadcrumbs": breadcrumbs,
#             "title": title,
#         },
#     )


# @staff_member_required
# def admin_order_pdf(request, order_id):
#     order = get_object_or_404(
#         Order.objects.select_related("delivery_method").prefetch_related(
#             "items__product", "items"
#         ),
#         id=order_id,
#     )

#     # Подсчет общего количества товаров и позиций
#     total_quantity = sum(
#         item.quantity for item in order.items.all()
#     )  # Общее количество товаров
#     total_items = order.items.count()  # Общее количество позиций
#     logo_path = request.build_absolute_uri(static("img/logo.png"))

#     html = render_to_string(
#         "orders/order/pdf.html",
#         {
#             "order": order,
#             "total_quantity": total_quantity,
#             "total_items": total_items,
#             "logo_path": logo_path,
#         },
#     )

#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
#     weasyprint.HTML(string=html).write_pdf(
#         response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
#     )
#     return response






# from cart.cart import Cart
# from django.shortcuts import get_object_or_404, render, redirect
# from .forms import OrderCreateForm
# from .models import OrderItem, Order
# from home.models import Category, Politica_firm, Uslovie_firm, Size, Product, ProductPrice  # Добавлен импорт ProductPrice
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from django.contrib.admin.views.decorators import staff_member_required
# import weasyprint
# from django.conf import settings
# from django.templatetags.static import static
# from .tasks import handle_order_created
# import os


# def order_create(request):
#     categories = Category.objects.all()
#     cart = Cart(request)
#     # get_root_catalog = categories.first().get_absolute_url()
#     # Добавляем проверку: если категорий нет, устанавливаем fallback на главную страницу
#     first_category = categories.first()
#     if first_category:
#         get_root_catalog = first_category.get_absolute_url()
#     else:
#         get_root_catalog = "/"  # Или reverse('home:index') если у тебя есть именованный URL для главной
#     politica = Politica_firm.objects.first()
#     uslovia = Uslovie_firm.objects.first()

#     # Проверка на наличие товаров в корзине
#     if not cart or not any(item["quantity"] > 0 for item in cart):
#         return redirect(get_root_catalog)

#     breadcrumbs = [{"name": "Оформление заказа", "slug": "/orders/"}]

#     if request.method == "POST":
#         form = OrderCreateForm(request.POST, user=request.user)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.user = request.user
#             order.save()

#             order_items = []

#             # Собираем идентификаторы продуктов и размеры
#             product_ids = [int(item["product_id"]) for item in cart]
#             size_titles = [item["size"] for item in cart]

#             # Получаем все продукты и размеры за один запрос
#             products = Product.objects.filter(id__in=product_ids).select_related(
#                 "category"
#             )
#             sizes = Size.objects.filter(title__in=size_titles)

#             # Создаем словари для быстрого доступа
#             product_dict = {product.id: product for product in products}
#             size_dict = {size.title: size for size in sizes}

#             for item in cart:
#                 # Получаем экземпляры продукта и размера
#                 product_instance = product_dict.get(int(item["product_id"]))
#                 size_instance = size_dict.get(item["size"])

#                 if product_instance and size_instance:
#                     # Получаем соответствующий ProductPrice
#                     try:
#                         product_price = ProductPrice.objects.get(
#                             product=product_instance, size=size_instance
#                         )
#                         order_item = OrderItem(
#                             order=order,
#                             product_price=product_price,  # Используем product_price вместо product и size
#                             price=item["price"],
#                             quantity=item["quantity"],
#                         )
#                         order_items.append(order_item)
#                     except ProductPrice.DoesNotExist:
#                         # Обработка случаев, когда цена продукта для данного размера не найдена
#                         print(f"ProductPrice not found for product_id: {item['product_id']}, size: {item['size']}")
#                 else:
#                     # Обработка случаев, когда продукт или размер не найдены
#                     print(f"Product or size not found for item: {item}")

#             # Сохраняем все элементы заказа за один раз
#             if order_items:  # Сохраняем только если есть элементы
#                 OrderItem.objects.bulk_create(order_items)

#             # Очистить корзину
#             cart.clear()

#             # Вызов функции обработки события
#             handle_order_created.delay(order.id)

#             return render(request, "orders/order/checkout_finish_page.html")
#     else:
#         form = OrderCreateForm(user=request.user)

#     # Добавлено: передача title в контекст
#     title = breadcrumbs[0]["name"] if breadcrumbs else "Оформление заказа"

#     return render(
#         request,
#         "orders/order/checkout_page.html",
#         {
#             "cart": cart,
#             "form": form,
#             "categories": categories,
#             "politica": politica,
#             "uslovia": uslovia,
#             "breadcrumbs": breadcrumbs,
#             "title": title,
#         },
#     )


# # @staff_member_required
# # def admin_order_pdf(request, order_id):
# #     order = get_object_or_404(
# #         Order.objects.select_related("delivery_method").prefetch_related(
# #             "items__product_price__product", "items__product_price__size"  # Обновлено: используем product_price для select_related
# #         ),
# #         id=order_id,
# #     )

# #     # Подсчет общего количества товаров и позиций
# #     total_quantity = sum(
# #         item.quantity for item in order.items.all()
# #     )  # Общее количество товаров
# #     total_items = order.items.count()  # Общее количество позиций
# #     logo_path = request.build_absolute_uri(static("img/logo.png"))

# #     html = render_to_string(
# #         "orders/order/pdf.html",
# #         {
# #             "order": order,
# #             "total_quantity": total_quantity,
# #             "total_items": total_items,
# #             "logo_path": logo_path,
# #         },
# #     )

# #     response = HttpResponse(content_type="application/pdf")
# #     response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
# #     weasyprint.HTML(string=html).write_pdf(
# #         response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
# #     )
# #     return response


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
#     if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT: # Проверяем, определен ли STATIC_ROOT
#         file_path = os.path.join(settings.STATIC_ROOT, filename)
#         if os.path.exists(file_path):
#             return file_path
#     return None



# @staff_member_required
# def admin_order_pdf(request, order_id):
#     order = get_object_or_404(
#         Order.objects.select_related("delivery_method").prefetch_related(
#             "items__product_price__product", "items__product_price__size"
#         ),
#         id=order_id,
#     )

#     total_quantity = sum(item.quantity for item in order.items.all())
#     total_items = order.items.count()

#     # Используем get_static_file_path для получения пути к логотипу
#     logo_path = get_static_file_path("img/logo.png")

#     html = render_to_string(
#         "orders/order/pdf.html",
#         {
#             "order": order,
#             "total_quantity": total_quantity,
#             "total_items": total_items,
#             "logo_path": logo_path,  # Передаем logo_uri в шаблон
#         },
#     )

#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = f"filename=order_{order.id}.pdf"

#     # Получаем путь к CSS-файлу
#     css_path = get_static_file_path("css/pdf.css")
#     stylesheets = []
#     if css_path:
#         stylesheets.append(weasyprint.CSS(filename=css_path))

#     weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
#     return response






# from cart.cart import Cart
# from django.shortcuts import get_object_or_404, render, redirect
# from .forms import OrderCreateForm
# from .models import OrderItem, Order
# from home.models import Category, Politica_firm, Uslovie_firm, Size, Product, ProductPrice  # Добавлен импорт ProductPrice
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from django.contrib.admin.views.decorators import staff_member_required
# import weasyprint
# from django.conf import settings
# from django.templatetags.static import static
# from .tasks import handle_order_created
# import os


# def order_create(request):
#     categories = Category.objects.all()
#     cart = Cart(request)
#     # get_root_catalog = categories.first().get_absolute_url()
#     # Добавляем проверку: если категорий нет, устанавливаем fallback на главную страницу
#     first_category = categories.first()
#     if first_category:
#         get_root_catalog = first_category.get_absolute_url()
#     else:
#         get_root_catalog = "/"  # Или reverse('home:index') если у тебя есть именованный URL для главной
#     politica = Politica_firm.objects.first()
#     uslovia = Uslovie_firm.objects.first()

#     # Проверка на наличие товаров в корзине
#     if not cart or not any(item["quantity"] > 0 for item in cart):
#         return redirect(get_root_catalog)

#     breadcrumbs = [{"name": "Оформление заказа", "slug": "/orders/"}]

#     if request.method == "POST":
#         form = OrderCreateForm(request.POST, user=request.user)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.user = request.user
#             order.save()

#             order_items = []

#             # Собираем идентификаторы продуктов и размеры
#             product_ids = [int(item["product_id"]) for item in cart]
#             size_titles = [item["size"] for item in cart]

#             # Получаем все продукты и размеры за один запрос
#             products = Product.objects.filter(id__in=product_ids).select_related(
#                 "category"
#             )
#             sizes = Size.objects.filter(title__in=size_titles)

#             # Создаем словари для быстрого доступа
#             product_dict = {product.id: product for product in products}
#             size_dict = {size.title: size for size in sizes}

#             for item in cart:
#                 # Получаем экземпляры продукта и размера
#                 product_instance = product_dict.get(int(item["product_id"]))
#                 size_instance = size_dict.get(item["size"])

#                 if product_instance and size_instance:
#                     # Получаем соответствующий ProductPrice
#                     try:
#                         product_price = ProductPrice.objects.get(
#                             product=product_instance, size=size_instance
#                         )
#                         order_item = OrderItem(
#                             order=order,
#                             product_price=product_price,  # Используем product_price вместо product и size
#                             price=item["price"],
#                             quantity=item["quantity"],
#                         )
#                         order_items.append(order_item)
#                     except ProductPrice.DoesNotExist:
#                         # Обработка случаев, когда цена продукта для данного размера не найдена
#                         print(f"ProductPrice not found for product_id: {item['product_id']}, size: {item['size']}")
#                 else:
#                     # Обработка случаев, когда продукт или размер не найдены
#                     print(f"Product or size not found for item: {item}")

#             # Сохраняем все элементы заказа за один раз
#             for order_item in order_items:
#                 order_item.save()

#             # Очистить корзину
#             cart.clear()

#             # Вызов функции обработки события
#             handle_order_created.delay(order.id)

#             return render(request, "orders/order/checkout_finish_page.html")
#     else:
#         form = OrderCreateForm(user=request.user)

#     # Добавлено: передача title в контекст
#     title = breadcrumbs[0]["name"] if breadcrumbs else "Оформление заказа"

#     return render(
#         request,
#         "orders/order/checkout_page.html",
#         {
#             "cart": cart,
#             "form": form,
#             "categories": categories,
#             "politica": politica,
#             "uslovia": uslovia,
#             "breadcrumbs": breadcrumbs,
#             "title": title,
#         },
#     )



# @staff_member_required
# def admin_order_pdf(request, order_id):
#     order = get_object_or_404(
#         Order.objects.select_related("delivery_method").prefetch_related(
#             "items__product_price__product", "items__product_price__size"  # Обновлено: используем product_price для select_related
#         ),
#         id=order_id,
#     )

#     # Подсчет общего количества товаров и позиций
#     total_quantity = sum(
#         item.quantity for item in order.items.all()
#     )  # Общее количество товаров
#     total_items = order.items.count()  # Общее количество позиций
#     logo_path = settings.STATIC_ROOT / 'img/logo.png'

#     html = render_to_string(
#         "orders/order/pdf.html", 
#         {
#             "order": order,
#             "total_quantity": total_quantity,
#             "total_items": total_items,
#             "logo_path": logo_path, 
#         },
#     )

#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
#     weasyprint.HTML(string=html).write_pdf(
#         response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
#     )
#     return response





from cart.cart import Cart
from django.shortcuts import get_object_or_404, render, redirect
from .forms import OrderCreateForm
from .models import OrderItem, Order
from home.models import Category, Politica_firm, Uslovie_firm, Size, Product, ProductPrice  # Добавлен импорт ProductPrice
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint
from django.conf import settings
from django.templatetags.static import static
from .tasks import handle_order_created


def order_create(request):
    categories = Category.objects.all()
    cart = Cart(request)
    # get_root_catalog = categories.first().get_absolute_url()
    # Добавляем проверку: если категорий нет, устанавливаем fallback на главную страницу
    first_category = categories.first()
    if first_category:
        get_root_catalog = first_category.get_absolute_url()
    else:
        get_root_catalog = "/"  # Или reverse('home:index') если у тебя есть именованный URL для главной
    politica = Politica_firm.objects.first()
    uslovia = Uslovie_firm.objects.first()

    # Итерируем по корзине заранее для очистки и сбора removed_items
    list(cart)  # Вызывает __iter__, удаляет несуществующие товары и заполняет removed_items
    removed_items = cart.get_removed_items()  # Получаем и очищаем список

    # Проверка на наличие товаров в корзине
    if not cart or not any(item["quantity"] > 0 for item in cart):
        return redirect(get_root_catalog)

    breadcrumbs = [{"name": "Оформление заказа", "slug": "/orders/"}]

    if request.method == "POST":
        form = OrderCreateForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            order_items = []

            # Собираем идентификаторы продуктов и размеры
            product_ids = [int(item["product_id"]) for item in cart]
            size_titles = [item["size"] for item in cart]

            # Получаем все продукты и размеры за один запрос
            products = Product.objects.filter(id__in=product_ids).select_related(
                "category"
            )
            sizes = Size.objects.filter(title__in=size_titles)

            # Создаем словари для быстрого доступа
            product_dict = {product.id: product for product in products}
            size_dict = {size.title: size for size in sizes}

            for item in cart:
                # Получаем экземпляры продукта и размера
                product_instance = product_dict.get(int(item["product_id"]))
                size_instance = size_dict.get(item["size"])

                if product_instance and size_instance:
                    # Получаем соответствующий ProductPrice
                    try:
                        product_price = ProductPrice.objects.get(
                            product=product_instance, size=size_instance
                        )
                        order_item = OrderItem(
                            order=order,
                            product_price=product_price,  # Используем product_price вместо product и size
                            price=item["price"],
                            quantity=item["quantity"],
                        )
                        order_items.append(order_item)
                    except ProductPrice.DoesNotExist:
                        # Обработка случаев, когда цена продукта для данного размера не найдена
                        print(f"ProductPrice not found for product_id: {item['product_id']}, size: {item['size']}")
                else:
                    # Обработка случаев, когда продукт или размер не найдены
                    print(f"Product or size not found for item: {item}")

            # Сохраняем все элементы заказа за один раз
            for order_item in order_items:
                order_item.save()

            # Очистить корзину
            cart.clear()

            # Вызов функции обработки события
            handle_order_created.delay(order.id)

            return render(request, "orders/order/checkout_finish_page.html")
    else:
        form = OrderCreateForm(user=request.user)

    # Добавлено: передача title в контекст
    title = breadcrumbs[0]["name"] if breadcrumbs else "Оформление заказа"

    return render(
        request,
        "orders/order/checkout_page.html",
        {
            "cart": cart,
            "form": form,
            "categories": categories,
            "politica": politica,
            "uslovia": uslovia,
            "breadcrumbs": breadcrumbs,
            "title": title,
            "removed_items": removed_items,  # Добавлено для уведомлений о удалённых товарах
        },
    )



@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("delivery_method").prefetch_related(
            "items__product_price__product", "items__product_price__size"  # Обновлено: используем product_price для select_related
        ),
        id=order_id,
    )

    # Подсчет общего количества товаров и позиций
    total_quantity = sum(
        item.quantity for item in order.items.all()
    )  # Общее количество товаров
    total_items = order.items.count()  # Общее количество позиций
    logo_path = settings.STATIC_ROOT / 'img/logo.png'

    html = render_to_string(
        "orders/order/pdf.html", 
        {
            "order": order,
            "total_quantity": total_quantity,
            "total_items": total_items,
            "logo_path": logo_path, 
        },
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
    )
    return response
