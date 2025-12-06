from django.shortcuts import render, get_object_or_404
from .models import (
    Category,
    Product,
    News,
    SizeTable,
    ImageSliderHome,
    DeliveryInfo,
    Review,
    ReviewImage,
    ProductPrice,
)
from cart.forms import CartAddProductForm
from .forms import ReviewForm
from django.db.models import Case, When, Min, Sum, Q
from orders.models import OrderItem
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import ContactForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.core.cache import cache
from django.shortcuts import reverse, redirect
from django.http import JsonResponse
from django.utils import timezone
from .tasks import process_images
import base64
from django.core.files.storage import default_storage as storage

class HomeView(ListView):
    template_name = "home/home_page.html"
    context_object_name = "products"  # Имя для списка продуктов в шаблоне
    extra_context = {"title": "Главная страница"}  # Дополнительный контекст

    def get_queryset(self):
        # Получаем самые продаваемые товары: агрегируем по ID и названию продукта через product_price
        top_selling_products = (
            OrderItem.objects.values(
                "product_price__product__id",  # Путь: OrderItem -> ProductPrice -> Product -> id
                "product_price__product__title"  # Путь: OrderItem -> ProductPrice -> Product -> title
            )
            .annotate(total_quantity=Sum("quantity"))  # Суммируем количество
            .order_by("-total_quantity")[:8]  # Топ-8 по убыванию продаж
        )

        # Извлекаем ID товаров в порядке продаж
        product_ids = [item["product_price__product__id"] for item in top_selling_products]

        # Получаем полные объекты продуктов с оптимизацией запросов
        products = (
            Product.objects.filter(id__in=product_ids)
            .select_related("category")  # Оптимизация для категории
            .prefetch_related("product_prices", "images")  # Оптимизация для цен и изображений
            .annotate(min_price=Min("product_prices__price"))  # Минимальная цена для каждой вариации
        )

        # Сортируем продукты в порядке популярности (как в top_selling_products)
        products = sorted(products, key=lambda p: product_ids.index(p.id))

        return products

    def get_context_data(self, **kwargs):
        # Здесь можно добавить дополнительный контекст, если нужно
        context = super().get_context_data(**kwargs)
        # Например, добавить слайдер или отзывы
        context['slider_image'] = ImageSliderHome.objects.all()  # Если у вас есть слайдер
       

        # Получаем все размеры и цены для всех продуктов 
        products = context["products"]
        product_ids = [product.id for product in products]
        sizes = ProductPrice.objects.filter(product_id__in=product_ids).select_related(
            "size"
        )

        # Создаем словарь для быстрого доступа к размерам и ценам
        size_price_map = {}
        for size in sizes:
            if size.product_id not in size_price_map:
                size_price_map[size.product_id] = []
            size_price_map[size.product_id].append((size.size.title, size.price))

        # Создаем формы для добавления в корзину
        context["cart_product_form"] = [
            (
                product,
                CartAddProductForm(
                    product=product, sizes=size_price_map.get(product.id, [])
                ),
            )
            for product in products
        ]

        return context


class ProductListView(ListView):
    model = Product
    template_name = "home/category_page.html"
    context_object_name = "products"
    paginate_by = 30  # Значение по умолчанию для количества продуктов на странице

    def get_queryset(self):
        # Получаем категорию по слагу
        slug = self.kwargs.get("slug")
        self.category = get_object_or_404(Category, slug=slug)

        # Фильтруем продукты по выбранной категории
        products = (
            Product.objects.filter(category=self.category, is_hidden=False)
            .prefetch_related(
                "product_prices__size",  # Предварительная загрузка цен и их размеров
                "images",  # Предварительная загрузка изображений
            )
            .select_related("category")
            .annotate(min_price=Min("product_prices__price"))
            )  # Предварительная загрузка категории продукта

        # Обработка сортировки
        sort_by = self.request.GET.get("sort", "created")
        if sort_by == "min_price":
            products = products.order_by("min_price")
        elif sort_by == "-min_price":
            products = products.order_by("-min_price")
        else:
            products = products.order_by("-created")

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        
        # Получаем корневую категорию
        root_category = self.category.get_root()
        
        # Получаем все нужные данные категорий за один запрос
        categories = Category.objects.filter(
            tree_id=root_category.tree_id
        ).order_by('lft')
        
        # Получаем детей текущей категории
        context["get_children_cat"] = [
            cat for cat in categories 
            if cat.parent_id == self.category.pk
        ]
        
        # Получаем потомков корневой категории
        context["get_descendants_cat"] = [
            cat for cat in categories 
            if cat.level == root_category.level + 1
        ]
        
        context["get_root_cat"] = root_category
        context["breadcrumbs"] = self.category.get_ancestors(include_self=True)

        # Получаем все размеры и цены для всех продуктов
        products = context["products"]
        product_ids = [product.id for product in products]
        sizes = ProductPrice.objects.filter(product_id__in=product_ids).select_related(
            "size"
        )

        # Создаем словарь для быстрого доступа к размерам и ценам
        size_price_map = {}
        for size in sizes:
            if size.product_id not in size_price_map:
                size_price_map[size.product_id] = []
            size_price_map[size.product_id].append((size.size.title, size.price))

        # Создаем формы для добавления в корзину
        context["cart_product_form"] = [
            (
                product,
                CartAddProductForm(
                    product=product, sizes=size_price_map.get(product.id, [])
                ),
            )
            for product in products
        ]

        # Устанавливаем количество продуктов на странице
        per_page = self.request.GET.get("per_page", self.paginate_by)
        context["per_page"] = per_page

        # Новая логика для ограниченной пагинации
        paginator = context["paginator"]  # Получаем пагинатор из ListView
        page = context["page_obj"]  # Текущая страница
        pages_to_show = 5  # Количество страниц для показа (текущая + вокруг неё; измените на нужное, например, 7)

        # Вычисляем диапазон: текущая страница в центре, если возможно
        half = pages_to_show // 2
        start_page = max(1, page.number - half)
        end_page = min(paginator.num_pages, page.number + half)

        # Корректируем, если диапазон меньше желаемого (например, в начале/конце)
        if end_page - start_page < pages_to_show - 1:
            if start_page == 1:
                end_page = min(paginator.num_pages, start_page + pages_to_show - 1)
            elif end_page == paginator.num_pages:
                start_page = max(1, end_page - pages_to_show + 1)

        # Передаём ограниченный диапазон в контекст
        context["page_range"] = range(start_page, end_page + 1)

        # # Флаги для показа "Первой" и "Последней" с "..." (если диапазон обрезан)
        # context["show_first"] = start_page > 1
        # context["show_last"] = end_page < paginator.num_pages

        return context

    def get_paginate_by(self, request):
        per_page = self.request.GET.get(
            "per_page", self.paginate_by
        )  # Получаем значение per_page из GET-запроса
        if isinstance(per_page, str) and per_page.isdigit():
            return int(per_page)
        return self.paginate_by  # Вернуть значение по умолчанию



class ProductDetailView(DetailView):
    model = Product
    template_name = "home/product_page.html"
    context_object_name = "product"

    def get_queryset(self):
        # Используем select_related для загрузки связанной категории
        return Product.objects.select_related("category").prefetch_related(
            "product_prices", "images"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Получить размеры и цены для продукта (исправлено: size__title вместо size__name)
        sizes_prices = list(
            product.product_prices.select_related("size").values_list(
                "size__title", "price"
            )  # size__title, так как поле в Size называется title
        )  # Список [(size_title, price), ...]

        context["cart_product_form"] = CartAddProductForm(sizes=sizes_prices)

        # Получаем хлебные крошки из категории и преобразуем в список
        breadcrumbs = list(
            product.category.get_breadcrumbs()
        )  # Преобразуем TreeQuerySet в список

        # Добавляем текущий продукт в хлебные крошки
        breadcrumbs.append({"name": product.title, "slug": product.get_absolute_url()})

        # Устанавливаем хлебные крошки в контекст
        context["breadcrumbs"] = breadcrumbs
        return context

    def get_object(self, queryset=None):
        # Переопределяем метод, чтобы добавить проверку на is_hidden
        obj = super().get_object(queryset)
        if obj.is_hidden:
            raise Http404("Product not found")
        return obj


class NewsListView(ListView):
    model = News
    template_name = "home/news_page.html"
    context_object_name = "news"  # Имя контекста для списка новостей
    extra_context = {"title": "Новости"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context["breadcrumbs"] = [
            {"name": "Новости", "slug": "/news/"},  # Страница новостей
        ]

        return context


class SizeTableListView(ListView):
    model = SizeTable
    template_name = "home/size_table_page.html"
    context_object_name = "size_table"  # Имя контекста для списка размеров
    extra_context = {"title": "Размерная таблица"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context["breadcrumbs"] = [
            {"name": "Размерная таблица", "slug": "/size_table/"},  # Страница размеров
        ]

        return context


class DeliveryView(ListView):
    model = DeliveryInfo
    template_name = "home/delivery_page.html"
    context_object_name = "delivery_info"
    extra_context = {"title": "Доставка"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context["breadcrumbs"] = [
            {"name": "Доставка", "slug": "/delivery/"},  # Страница доставка
        ]

        return context


class ContactsView(FormView):
    form_class = ContactForm
    template_name = "home/contacts_page.html"
    extra_context = {"title": "Контакты"}
    success_url = reverse_lazy("home:contacts")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context["breadcrumbs"] = [
            {"name": "Контакты", "slug": "/contacts/"},  # Страница доставка
        ]

        return context

    def get_form_kwargs(self):
        # Получаем исходные аргументы формы
        kwargs = super().get_form_kwargs()
        # Добавляем пользователя в аргументы формы
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Проверяем, аутентифицирован ли пользователь
        if self.request.user.is_authenticated:
            first_name = form.cleaned_data["first_name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
        else:
            first_name = form.cleaned_data["first_name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]

        content = form.cleaned_data["content"]

        # Отправка сообщения
        subject = f"Новое сообщение от {first_name}"
        message_body = (
            f"Имя: {first_name}\n"
            f"Email: {email}\n"
            f"Телефон: {phone}\n"
            f"Сообщение:\n{content}"
        )
        admin_email = settings.EMAIL_HOST_USER

        send_mail(subject, message_body, settings.DEFAULT_FROM_EMAIL, [admin_email])

        messages.success(self.request, "Ваше сообщение успешно отправлено!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Ошибка при отправке сообщения. Пожалуйста, проверьте форму."
        )
        return super().form_invalid(form)




class ReviewsView(LoginRequiredMixin, FormView, ListView):
    form_class = ReviewForm
    template_name = "home/reviews_page.html"
    success_url = reverse_lazy("home:reviews")
    context_object_name = "reviews"
    extra_context = {"title": "Отзывы"}
    paginate_by = 5

    def get_queryset(self):
        return (
            Review.objects.all()
            .select_related("user")
            .prefetch_related("images")  # Prefetch for images
            .order_by("-created_at")
        )

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page", self.paginate_by)
        if isinstance(per_page, str) and per_page.isdigit():
            return int(per_page)
        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumbs": [{"name": "Отзывы", "slug": "/reviews/"}],
                "user": self.request.user,
                "form": self.get_form(),
            }
        )

        reviews = context['reviews']  # Твой queryset отзывов
    
        # Фильтр изображений: только существующие
        for review in reviews:
            # Проверяем и отбираем только существующие файлы
            review.existing_images = [
                img for img in review.images.all()
                if storage.exists(img.image.name)  # Проверка существования файла
            ]
        
        context['reviews'] = reviews
        page_obj = context.get("page_obj")
        if page_obj:
            current_page = page_obj.number
            total_pages = page_obj.paginator.num_pages
            range_size = 5
            
            start_page = max(1, current_page - range_size // 2)
            end_page = min(total_pages, start_page + range_size - 1)
            start_page = max(1, end_page - range_size + 1)
            
            context["page_range"] = list(range(start_page, end_page + 1))
            context["per_page"] = self.get_paginate_by(None)
        
        return context

    def form_valid(self, form):
        # ДОБАВЛЕНО: Проверка на недавний дублированный отзыв (предотвращает спам)
        recent_reviews = Review.objects.filter(
            user=self.request.user,
            content=form.cleaned_data['content'],
            created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        )
        if recent_reviews.exists():
            return JsonResponse({
                'success': False,
                'message': 'Похожий отзыв уже отправлен. Подождите или отредактируйте.'
            }, status=400)
        
        review = form.save(commit=False)
        review.user = self.request.user
        review.save()

        images = self.request.FILES.getlist("images")
        # Собираем данные файлов: сериализуемые словари (name + base64 content)
        images_data = []
        for img in images:
            img.seek(0)  # Убеждаемся, что файл читается с начала
            content = img.read()
            images_data.append({
                'name': img.name,
                'content': base64.b64encode(content).decode('utf-8'),  # Сериализуемый string
                'content_type': img.content_type or 'image/jpeg'  # Добавлено для метаданных
            })

        # Запускаем фоновую обработку с передачей данных
        process_images.delay(review.id, images_data)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Отзыв успешно отправлен! Изображения обрабатываются...',
                'redirect_url': f"{reverse('home:reviews')}?page=1"
            })
        else:
            return redirect(f"{reverse('home:reviews')}?page=1")

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Ошибка в форме. Проверьте данные.',
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)



class Search(ListView):
    model = Product
    template_name = "home/search.html"
    context_object_name = "products"
    paginate_by = 30

    def get_queryset(self):
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            # Полнотекстовый поиск: используем annotate для search_vector, затем filter (избегаем @@, чтобы избежать SyntaxError в некоторых средах)
            products = (
                Product.objects.annotate(
                    search=SearchVector(
                        "title", "category__name", "description", "article_number"
                    )
                )
                .filter(search=SearchQuery(search_query), is_hidden=False)
                .annotate(
                    min_price=Min(
                        "product_prices__price"
                    )  # Аннотация min_price всегда, если есть поиск (для сортировки)
                )
                .prefetch_related(
                    "product_prices__size",  # Загружаем цены и размеры заранее (без дополнительных запросов)
                    "images",  # Загружаем изображения
                )
                .select_related("category")
            )  # Загружаем категорию

            # Сортировка (только если есть товары)
            sort_by = self.request.GET.get("sort", "created")
            if sort_by == "min_price":
                products = products.order_by("min_price")
            elif sort_by == "-min_price":
                products = products.order_by("-min_price")
            else:
                products = products.order_by("-created")  # По умолчанию -created
        else:
            # Если поиск не задан, пустой QuerySet (главная страница)
            products = Product.objects.none()

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("search", "").strip()
        products = context["products"]  # Page.object_list (список объектов)

        if search_query:
            context["category"] = f'Результаты поиска по "{search_query}"'
            context["get_children_cat"] = []
            context["breadcrumbs"] = [
                {"name": f'Результаты поиска по "{search_query}"', "url": None},
            ]

            if not products:
                context["no_results"] = True
                context["no_results_message"] = (
                    f'К сожалению, по Вашему запросу "{search_query}" ничего не найдено.'
                )
            else:
                context["no_results"] = False
        else:
            context["category"] = "Каталог"
            context["get_children_cat"] = Category.objects.filter(parent=None)
            context["breadcrumbs"] = [
                {"name": "Каталог", "url": "/"},
            ]

        # Категории для боковой панели
        context["get_descendants_cat"] = Category.objects.filter(
            parent__isnull=False, parent__parent=None
        )
        context["get_root_cat"] = None

        # Строим size_price_map из уже загруженных данных (prefetch_related), без дополнительных запросов
        if products:
            size_price_map = {
                product.id: [
                    (pp.size.title, pp.price) for pp in product.product_prices.all()
                ]
                for product in products
            }

            context["cart_product_form"] = [
                (
                    product,
                    CartAddProductForm(
                        product=product, sizes=size_price_map.get(product.id, [])
                    ),
                )
                for product in products
            ]
        else:
            context["cart_product_form"] = []

        # per_page
        if products:
            context["per_page"] = self.get_paginate_by(context["products"])
        else:
            context["per_page"] = self.paginate_by

        return context

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page", self.paginate_by)
        if isinstance(per_page, str) and per_page.isdigit():
            return int(per_page)
        return self.paginate_by
