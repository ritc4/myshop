from django.shortcuts import render

def home(request):
    return render(request, 'home/home_page.html')


def category(request):
    return render(request, 'home/category_page.html')


def product(request):
    return render(request, 'home/product_page.html')

