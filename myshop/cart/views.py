from django.shortcuts import render
from home.models import Category

def cart_views(request):
    categories = Category.objects.all()
    return render(request,'cart/cart_page.html', {'categories':categories})

