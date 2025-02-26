from django.shortcuts import render,get_object_or_404
from .models import Category,Product,News,SizeTable
from cart.forms import CartAddProductForm
from django.db.models import Sum
from orders.models import OrderItem
from django.views.generic import ListView


def home(request):
    categories = Category.objects.all()
    # Получаем самые продаваемые товары
    top_selling_products = (
        OrderItem.objects
        .values('product__id', 'product__title')  # Получаем ID и название товара
        .annotate(total_quantity=Sum('quantity'))  # Суммируем количество
        .order_by('-total_quantity')[:8]  # Ограничиваем до 8 самых продаваемых
    )

    # Получаем сами продукты по их ID
    product_ids = [item['product__id'] for item in top_selling_products]
    products = Product.objects.filter(id__in=product_ids)

    # Создаем формы для добавления в корзину
    cart_product_form = [(product, CartAddProductForm(product=product)) for product in products]

    # Обрабатываем продукты для нахождения минимальной цены и получения размеров
    for product in products:
        prices = product.product_prices.all()  # Получаем все цены для продукта
        if prices.exists():
            product.min_price = min(prices, key=lambda x: x.price).price
            product.min_price_size = min(prices, key=lambda x: x.price).size  # Получаем размер с минимальной ценой
        else:
            product.min_price = None
            product.min_price_size = None
    
    return render(request, 'home/home_page.html', {'categories':categories,'cart_product_form':cart_product_form})




class ProductListView(ListView):
    model = Product
    template_name = 'home/category_page.html'
    context_object_name = 'products'
    paginate_by = 30  # Количество продуктов на странице

    def get_queryset(self):
        # Получаем категорию по слагу
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)
        
        # Фильтруем продукты по выбранной категории
        products = Product.objects.filter(category=category, is_hidden=False).prefetch_related('product_prices__size')

        # Обрабатываем продукты для нахождения минимальной цены и получения размеров
        for product in products:
            prices = product.product_prices.all()  # Получаем все цены для продукта
            if prices.exists():
                product.min_price = min(prices, key=lambda x: x.price).price
                product.min_price_size = min(prices, key=lambda x: x.price).size  # Получаем размер с минимальной ценой
            else:
                product.min_price = None
                product.min_price_size = None

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['category'] = get_object_or_404(Category, slug=slug)
        context['categories'] = Category.objects.all()  # Получаем все категории
        context['get_root_cat'] = context['category'].get_root()  # Получаем корневую категорию
        context['get_children_cat'] = context['category'].get_children()  # Получаем дочерние категории
        context['get_descendants_cat'] = context['get_root_cat'].get_children()  # Получаем все дочерние категории корня
        
        # Создаем формы для добавления продуктов в корзину
        context['cart_product_form'] = [(product, CartAddProductForm(product=product)) for product in context['products']]
        
        return context


def product_detail(request,id,slug):
    product = get_object_or_404(Product,id=id,slug=slug,is_hidden=False)
    categories = Category.objects.all()  # Получаем все категории
    cart_product_form = CartAddProductForm(product=product)

    return render(request, 'home/product_page.html', 
        {'product': product, 
         'categories': categories,
         'cart_product_form':cart_product_form})


def news(request):
    categories = Category.objects.all()
    news = News.objects.all()
    return render(request, 'home/news_page.html',{'categories': categories,'news':news})

def size_table(request):
    categories = Category.objects.all()
    size_table = SizeTable.objects.all()
    return render(request, 'home/size_table_page.html',{'categories': categories,'size_table':size_table})







def registration(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/registration_page.html',{'categories': categories})

def login(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/login_page.html',{'categories': categories})


def reviews(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/reviews_page.html',{'categories': categories})

def contacts(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/contacts_page.html',{'categories': categories})

def delivery(request):
    categories = Category.objects.all()  # Получите все категории
    return render(request, 'home/delivery_page.html',{'categories': categories})
