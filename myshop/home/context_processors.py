from .models import Category

def breadcrumbs(request):
    # Получаем текущую категорию из URL
    category_slug = request.resolver_match.kwargs.get('slug')
    breadcrumbs = []

    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            breadcrumbs = category.get_breadcrumbs()
        except Category.DoesNotExist:
            pass

    return {'breadcrumbs': breadcrumbs}



def categories_processor(request):
    return {
        'categories': Category.objects.all()
        }