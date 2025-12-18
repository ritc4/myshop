# from django.urls import reverse
# from django.shortcuts import redirect
# from .models import Product, Category

# class SubdomainRedirectMiddleware:
#     """
#     Middleware для перенаправления поддоменов продуктов.
#     Пример: product-slug.cozy-opt.ru -> /product/product-slug/
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = request.get_host()
#         # Разбираем хост: sub.domain.com → ['sub', 'domain.com']
#         try:
#             subdomain, main_domain = host.split('.', 1)
#         except ValueError:
#             subdomain = None

#         if subdomain and '.' not in subdomain:
#             # Список игнорируемых поддоменов
#             ignored_subdomains = ['www', 'cozy-opt']
#             if subdomain not in ignored_subdomains:
#                 # Проверяем продукт с фильтром по is_hidden=False
#                 product = Product.objects.filter(slug=subdomain, is_hidden=False).first()
#                 if product:
#                     # URL для продукта
#                     redirect_url = reverse("home:product_detail", kwargs={"slug": product.slug, "id": product.id})
#                     # Полный URL с протоколом из запроса (http или https)
#                     full_redirect_url = f"{request.scheme}://{main_domain}{redirect_url}"
#                     return redirect(full_redirect_url, status=301)

#         # Если поддомен не найден или проигнорирован — обычный ответ
#         response = self.get_response(request)
#         return response
    


# class CategorySubdomainRedirectMiddleware:
#     """
#     Middleware для перенаправления поддоменов категорий.
#     Пример: category-slug.cozy-opt.ru -> /category/category-slug/
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = request.get_host()
#         # Разбираем хост: sub.domain.com → ['sub', 'domain.com']
#         try:
#             subdomain, main_domain = host.split('.', 1)
#         except ValueError:
#             subdomain = None

#         if subdomain and '.' not in subdomain:
#             # Список игнорируемых поддоменов
#             ignored_subdomains = ['www', 'cozy-opt']
#             if subdomain not in ignored_subdomains:
#                 # Проверяем категорию (без фильтра is_hidden, как в вашем исходном коде)
#                 category = Category.objects.filter(slug=subdomain).first()
#                 if category:
#                     # URL для категории
#                     redirect_url = reverse("home:category", kwargs={"slug": category.slug})
#                     # Полный URL с протоколом из запроса (http или https)
#                     full_redirect_url = f"{request.scheme}://{main_domain}{redirect_url}"
#                     return redirect(full_redirect_url, status=301)

#         # Если поддомен не найден или проигнорирован — обычный ответ
#         response = self.get_response(request)
#         return response





from django.urls import reverse
from django.shortcuts import redirect
from .models import Product, Category

# без кэша
class DynamicSubdomainRedirectMiddleware:
    """
    Middleware for redirecting subdomains (categories -> products, with priority on categories).
    Examples:
    - category-slug.cozy-opt.ru -> /category/category-slug/
    - product-slug.cozy-opt.ru -> /product/product-slug/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        try:
            subdomain, main_domain = host.split('.', 1)
        except ValueError:
            subdomain = None

        if subdomain and '.' not in subdomain:
            ignored_subdomains = ['www', 'cozy-opt']
            if subdomain not in ignored_subdomains:
                # Priority: Check categories (no is_hidden filter)
                category = Category.objects.filter(slug=subdomain).first()
                if category:
                    try:
                        redirect_url = reverse("home:category", kwargs={"slug": category.slug})
                        full_redirect_url = f"{request.scheme}://{main_domain}{redirect_url}"
                        return redirect(full_redirect_url, status=301)
                    except Exception:
                        pass  # Fallback: if reverse fails, continue

                # If category not found, check products (with is_hidden=False)
                product = Product.objects.filter(slug=subdomain, is_hidden=False).first()
                if product:
                    try:
                        redirect_url = reverse("home:product_detail", kwargs={"slug": product.slug, "id": product.id})
                        full_redirect_url = f"{request.scheme}://{main_domain}{redirect_url}"
                        return redirect(full_redirect_url, status=301)
                    except Exception:
                        pass  # Fallback

        response = self.get_response(request)
        return response





# from django.urls import reverse
# from django.shortcuts import redirect
# from django.core.cache import cache  # Используем настроенный Redis-кэш
# from .models import Product, Category

# def get_product_by_slug(slug):
#     """
#     Получить продукт по slug с кэшем в Redis.
#     Ключ: 'product_slug:{slug}', TTL: 3600 сек (1 час).
#     """
#     cache_key = f"product_slug:{slug}"
#     product = cache.get(cache_key)
#     if product is None:
#         product = Product.objects.filter(slug=slug, is_hidden=False).first()
#         if product:
#             cache.set(cache_key, product, timeout=3600)  # Кэш на 1 час; меняйте если нужно
#     return product

# def get_category_by_slug(slug):
#     """
#     Получить категорию по slug с кэшем в Redis.
#     Ключ: 'category_slug:{slug}', TTL: 3600 сек (1 час).
#     """
#     cache_key = f"category_slug:{slug}"
#     category = cache.get(cache_key)
#     if category is None:
#         category = Category.objects.filter(slug=slug).first()
#         if category:
#             cache.set(cache_key, category, timeout=3600)
#     return category

# class DynamicSubdomainRedirectMiddleware:
#     """
#     Middleware для перенаправления поддоменов (категории -> продукты).
#     Теперь с Redis-кэшем для масштабируемости.
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = request.get_host()
#         try:
#             subdomain, main_domain = host.split('.', 1)
#         except ValueError:
#             subdomain = None

#         if subdomain and '.' not in subdomain:
#             ignored_subdomains = ['www']
#             if subdomain not in ignored_subdomains:
#                 # Приоритет: категории, потом продукты
#                 category = get_category_by_slug(subdomain)
#                 if category:
#                     try:
#                         redirect_url = reverse("home:category", kwargs={"slug": category.slug})
#                         full_redirect_url = f"{request.scheme}://{main_domain}{redirect_url}"
#                         return redirect(full_redirect_url, status=301)
#                     except Exception:
#                         pass  # Для безопасности; лучше логировать в prod

#                 product = get_product_by_slug(subdomain)
#                 if product:
#                     try:
#                         redirect_url = reverse("home:product_detail", kwargs={"slug": product.slug, "id": product.id})
#                         full_redirect_url = f"{request.scheme}://{main_domain}{redirect_url}"
#                         return redirect(full_redirect_url, status=301)
#                     except Exception:
#                         pass

#         response = self.get_response(request)
#         return response
