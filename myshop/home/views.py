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
    products = Product.objects.filter(category=category, is_hidden=False)

    get_root_cat = category.get_root()  # Получаем корневую категорию
    get_children_cat = category.get_children()  # Получаем дочерние категории
    get_descendants_cat = get_root_cat.get_children()  # Получаем все дочерние категории корня
    cart_product_form = CartAddProductForm()

    return render(request,'home/category_page.html', 
                  {
                      'category': category,
                      'categories': categories,
                      'get_root_cat': get_root_cat,
                      'get_descendants_cat': get_descendants_cat,
                      'get_children_cat': get_children_cat,
                      'product': products,  # Изменено с 'product' на 'products'
                      'cart_product_form':cart_product_form})


def product_detail(request,id,slug):
    product = get_object_or_404(Product,id=id,slug=slug,is_hidden=False)
    categories = Category.objects.all()  # Получаем все категории
    size_product = product.size.all()
    cart_product_form = CartAddProductForm()

    return render(request, 'home/product_page.html', 
        {'product': product, 'categories': categories,
         'size_product':size_product,
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