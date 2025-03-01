from django.shortcuts import render,get_object_or_404
from .models import Category,Product,News,SizeTable,ImageSliderHome,DeliveryInfo
from cart.forms import CartAddProductForm
from django.db.models import Case, When,Min,Sum
from orders.models import OrderItem
from django.views.generic import ListView,DetailView



# class HomeView(ListView):
#     template_name = 'home/home_page.html'
#     context_object_name = 'products'  # Имя контекста для списка продуктов

#     def get_queryset(self):
#         # Получаем самые продаваемые товары
#         top_selling_products = (
#             OrderItem.objects
#             .values('product__id', 'product__title')  # Получаем ID и название товара
#             .annotate(total_quantity=Sum('quantity'))  # Суммируем количество
#             .order_by('-total_quantity')[:8]  # Ограничиваем до 8 самых продаваемых
#         )

#         # Получаем ID товаров в порядке их продаж
#         product_ids = [item['product__id'] for item in top_selling_products]

#          # Используем select_related и prefetch_related
#         products = (
#             Product.objects
#             .filter(id__in=product_ids)
#             .select_related('category')  # Загружаем связанную категорию
#             .prefetch_related('product_prices','images')
#             .annotate(min_price=Min('product_prices__price'))
#             .order_by(Case(*[When(id=prod_id, then=idx) for idx, prod_id in enumerate(product_ids)]))
#         )

#         return products

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['slider_image'] = ImageSliderHome.objects.all()

#         # Создаем формы для добавления в корзину
#         context['cart_product_form'] = [
#             (product, CartAddProductForm(product=product)) for product in context['products']
#             ]

#         return context


class HomeView(ListView):
    template_name = 'home/home_page.html'
    context_object_name = 'products'  # Имя контекста для списка продуктов

    def get_queryset(self):
        # Получаем самые продаваемые товары
        top_selling_products = (
            OrderItem.objects
            .values('product__id', 'product__title')  # Получаем ID и название товара
            .annotate(total_quantity=Sum('quantity'))  # Суммируем количество
            .order_by('-total_quantity')[:8]  # Ограничиваем до 8 самых продаваемых
        )

        # Получаем ID товаров в порядке их продаж
        product_ids = [item['product__id'] for item in top_selling_products]

        # Используем select_related и prefetch_related
        products = (
            Product.objects
            .filter(id__in=product_ids)
            .select_related('category')  # Загружаем связанную категорию
            .prefetch_related('product_prices', 'images')
            .annotate(min_price=Min('product_prices__price'))
        )

        # Сортируем продукты в том же порядке, что и в top_selling_products
        products = sorted(products, key=lambda p: product_ids.index(p.id))

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slider_image'] = ImageSliderHome.objects.all()

        # Создаем формы для добавления в корзину
        context['cart_product_form'] = [
            (product, CartAddProductForm(product=product)) for product in context['products']
        ]

        return context





# class ProductListView(ListView):
#     model = Product
#     template_name = 'home/category_page.html'
#     context_object_name = 'products'
#     paginate_by = 30  # Значение по умолчанию для количества продуктов на странице

#     def get_queryset(self):
#         # Получаем категорию по слагу
#         slug = self.kwargs.get('slug')
#         category = get_object_or_404(Category, slug=slug)

#         # Фильтруем продукты по выбранной категории
#         products = Product.objects.filter(category=category, is_hidden=False).prefetch_related('product_prices__size')

#         # Обработка сортировки
#         sort_by = self.request.GET.get('sort', 'created')  # По умолчанию сортируем по времени добавления
#         if sort_by == 'min_price':
#             products = products.annotate(min_price=Min('product_prices__price')).order_by('min_price')
#         elif sort_by == '-min_price':
#             products = products.annotate(min_price=Min('product_prices__price')).order_by('-min_price')
#         else:
#             products = products.annotate(min_price=Min('product_prices__price')).order_by('-created')

#         return products

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         slug = self.kwargs.get('slug')
#         context['category'] = get_object_or_404(Category, slug=slug)
#         context['get_root_cat'] = context['category'].get_root()  # Получаем корневую категорию
#         context['get_children_cat'] = context['category'].get_children()  # Получаем дочерние категории
#         context['get_descendants_cat'] = context['get_root_cat'].get_children()  # Получаем все дочерние категории корня
      


#         # Создаем формы для добавления продуктов в корзину
#         context['cart_product_form'] = [(product, CartAddProductForm(product=product)) for product in context['products']]

#         # Устанавливаем количество продуктов на странице
#         per_page = self.request.GET.get('per_page', self.paginate_by)  # Получаем значение per_page из GET-запроса
#         context['per_page'] = per_page

#         return context

#     def get_paginate_by(self, request):
#         per_page = self.request.GET.get('per_page', self.paginate_by)  # Получаем значение per_page из GET-запроса
#         if isinstance(per_page, str) and per_page.isdigit():
#             return int(per_page)
#         return self.paginate_by  # Вернуть значение по умолчанию



class ProductListView(ListView):
    model = Product
    template_name = 'home/category_page.html'
    context_object_name = 'products'
    paginate_by = 30  # Значение по умолчанию для количества продуктов на странице

    def get_queryset(self):
        # Получаем категорию по слагу
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)

        # Фильтруем продукты по выбранной категории
        products = Product.objects.filter(category=category, is_hidden=False).prefetch_related(
            'product_prices__size',  # Предварительная загрузка цен и их размеров
            'images'  # Предварительная загрузка изображений
        ).select_related('category')  # Предварительная загрузка категории продукта

        # Обработка сортировки
        sort_by = self.request.GET.get('sort', 'created')  # По умолчанию сортируем по времени добавления
        if sort_by == 'min_price':
            products = products.annotate(min_price=Min('product_prices__price')).order_by('min_price')
        elif sort_by == '-min_price':
            products = products.annotate(min_price=Min('product_prices__price')).order_by('-min_price')
        else:
            products = products.annotate(min_price=Min('product_prices__price')).order_by('-created')

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['category'] = get_object_or_404(Category, slug=slug)
        context['get_root_cat'] = context['category'].get_root()  # Получаем корневую категорию
        context['get_children_cat'] = context['category'].get_children()  # Получаем дочерние категории
        context['get_descendants_cat'] = context['get_root_cat'].get_children()  # Получаем все дочерние категории корня

        # Создаем формы для добавления продуктов в корзину
        context['cart_product_form'] = [
            (product, CartAddProductForm(product=product)) for product in context['products']
        ]

        # Устанавливаем количество продуктов на странице
        per_page = self.request.GET.get('per_page', self.paginate_by)  # Получаем значение per_page из GET-запроса
        context['per_page'] = per_page

        return context

    def get_paginate_by(self, request):
        per_page = self.request.GET.get('per_page', self.paginate_by)  # Получаем значение per_page из GET-запроса
        if isinstance(per_page, str) and per_page.isdigit():
            return int(per_page)
        return self.paginate_by  # Вернуть значение по умолчанию




# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'home/product_page.html'
#     context_object_name = 'product'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         product = self.object  # Получаем текущий продукт
#         context['cart_product_form'] = CartAddProductForm(product=product)  # Форма добавления в корзину
#         # Получаем хлебные крошки из категории и преобразуем в список
#         breadcrumbs = list(product.category.get_breadcrumbs())  # Преобразуем TreeQuerySet в список

#         # Добавляем текущий продукт в хлебные крошки
#         breadcrumbs.append({'name': product.title, 'slug': product.get_absolute_url()})

#         # Устанавливаем хлебные крошки в контекст
#         context['breadcrumbs'] = breadcrumbs
#         return context

#     def get_object(self, queryset=None):
#         # Переопределяем метод, чтобы добавить проверку на is_hidden
#         obj = super().get_object(queryset)
#         if obj.is_hidden:
#             raise Http404("Product not found")
#         return obj



class ProductDetailView(DetailView):
    model = Product
    template_name = 'home/product_page.html'
    context_object_name = 'product'

    def get_queryset(self):
        # Используем select_related для загрузки связанной категории
        return Product.objects.select_related('category').prefetch_related('product_prices', 'images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object  # Получаем текущий продукт
        context['cart_product_form'] = CartAddProductForm(product=product)  # Форма добавления в корзину
        
        # Получаем хлебные крошки из категории и преобразуем в список
        breadcrumbs = list(product.category.get_breadcrumbs())  # Преобразуем TreeQuerySet в список

        # Добавляем текущий продукт в хлебные крошки
        breadcrumbs.append({'name': product.title, 'slug': product.get_absolute_url()})

        # Устанавливаем хлебные крошки в контекст
        context['breadcrumbs'] = breadcrumbs
        return context

    def get_object(self, queryset=None):
        # Переопределяем метод, чтобы добавить проверку на is_hidden
        obj = super().get_object(queryset)
        if obj.is_hidden:
            raise Http404("Product not found")
        return obj


class NewsListView(ListView):
    model = News
    template_name = 'home/news_page.html'
    context_object_name = 'news'  # Имя контекста для списка новостей

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Новости', 'slug': '/news/'},  # Страница новостей
            ]
        
        return context
    


class SizeTableListView(ListView):
    model = SizeTable
    template_name = 'home/size_table_page.html'
    context_object_name = 'size_table'  # Имя контекста для списка размеров

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Размерная таблица', 'slug': '/size_table/'},  # Страница размеров
            ]

        return context


class DeliveryView(ListView):
    model = DeliveryInfo
    template_name = 'home/delivery_page.html'
    context_object_name = 'delivery_info'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Доставка', 'slug': '/delivery/'},  # Страница доставка
            ]

        return context


class ContactsView(ListView):
    model = DeliveryInfo
    template_name = 'home/contacts_page.html'
    context_object_name = ''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

         # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Контакты', 'slug': '/contacts/'},  # Страница доставка
            ]
        
        return context
    


class ReviewsView(ListView):
    model = DeliveryInfo
    template_name = 'home/reviews_page.html'
    context_object_name = ''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

         # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Отзывы', 'slug': '/reviews/'},  # Страница доставка
            ]
        
        return context
    


def registration(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/registration_page.html',{'categories': categories})

def login(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/login_page.html',{'categories': categories})



