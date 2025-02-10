from django.shortcuts import render,get_object_or_404
from .models import Category,Product


def home(request):
    categories = Category.objects.all()
    return render(request, 'home/home_page.html', {'categories':categories})

def get_category(request,slug):
    category = get_object_or_404(Category, slug=slug)
    categories = Category.objects.all()
    get_root_cat = category.get_root()
    get_children_cat = category.get_children()
    get_descendants_cat = get_root_cat.get_children()
    product = category.cat.filter(is_hidden=False)
    print(product)

    return render(request, 
    'home/category_page.html', {'category':category,
    'categories':categories,'get_root_cat':get_root_cat,
    'get_descendants_cat':get_descendants_cat,'get_children_cat':get_children_cat,'product':product})


def product_details(request,slug):
    product = get_object_or_404(Product,slug=slug)
    categories = Category.objects.all()  # Получаем все категории
    size_product = product.size.all()
    return render(request, 'home/product_page.html', {'product': product, 'categories': categories,'size_product':size_product})




def registration(request):
    return render(request, 'home/registration_page.html')

def login(request):
    return render(request, 'home/login_page.html')

def cart(request):
    categories = Category.objects.all() 
    return render(request, 'home/cart_page.html',{'categories': categories})

def checkout(request):
    return render(request, 'home/checkout_page.html')


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