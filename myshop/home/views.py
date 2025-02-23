from django.shortcuts import render,get_object_or_404
from .models import Category,Product
from cart.forms import CartAddProductForm


def home(request):
    categories = Category.objects.all()
    return render(request, 'home/home_page.html', {'categories':categories})




def product_list(request, slug):
    categories = Category.objects.all()  # Получаем все категории
    category = get_object_or_404(Category, slug=slug)  # Получаем категорию по слагу

    # Фильтруем продукты по выбранной категории
    products = Product.objects.filter(category=category, is_hidden=False).prefetch_related('product_prices__size')
    get_root_cat = category.get_root()  # Получаем корневую категорию
    get_children_cat = category.get_children()  # Получаем дочерние категории
    get_descendants_cat = get_root_cat.get_children()  # Получаем все дочерние категории корня
    cart_product_form = CartAddProductForm()

    # Обрабатываем продукты для нахождения минимальной цены и получения размеров
    for product in products:
        prices = product.product_prices.all()  # Получаем все цены для продукта
        if prices.exists():
            product.min_price = min(prices, key=lambda x: x.price).price
            product.min_price_size = min(prices, key=lambda x: x.price).size  # Получаем размер с минимальной ценой
        else:
            product.min_price = None
            product.min_price_size = None

    return render(request,'home/category_page.html', 
                  {
                      'category': category,
                      'categories': categories,
                      'get_root_cat': get_root_cat,
                      'get_descendants_cat': get_descendants_cat,
                      'get_children_cat': get_children_cat,
                      'products': products,  # Изменено с 'product' на 'products'
                      'cart_product_form':cart_product_form,
                      })


def product_detail(request,id,slug):
    product = get_object_or_404(Product,id=id,slug=slug,is_hidden=False)
    categories = Category.objects.all()  # Получаем все категории
    cart_product_form = CartAddProductForm(product=product)

    return render(request, 'home/product_page.html', 
        {'product': product, 
         'categories': categories,
         'cart_product_form':cart_product_form})








def registration(request):
    return render(request, 'home/registration_page.html')

def login(request):
    return render(request, 'home/login_page.html')

# def cart(request):
#     categories = Category.objects.all() 
#     return render(request, 'home/cart_page.html',{'categories': categories})

def checkout(request):
    categories = Category.objects.all()  # Получаем все категории
    return render(request, 'home/checkout_page.html',{'categories': categories})


def reviews(request):
    return render(request, 'home/reviews_page.html')

def conditions(request):
    return render(request, 'home/conditions_page.html')

def contacts(request):
    return render(request, 'home/contacts_page.html')

def delivery(request):
    return render(request, 'home/delivery_page.html')

def news(request):
    return render(request, 'home/news_page.html')