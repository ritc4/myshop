from .models import Category
from django.conf import settings



def categories_processor(request):
    return {
        'categories': Category.objects.all()
        }



def email(request):
    return {
        'site_email': settings.DEFAULT_FROM_EMAIL,
    }


def admin_phone(request):
    return {
        'admin_phone': settings.ADMIN_PHONE,
    }