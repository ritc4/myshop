"""
URL configuration for myshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib.sitemaps.views import sitemap
from sitemaps import sitemaps  # Импорт из корневого sitemaps.py

# Добавляем импорт для robots.txt view
from django.http import HttpResponse



def robots_txt(request):
    """
    Возвращает содержимое robots.txt.
    Настройте правила под ваш сайт: запреты/разрешения для ботов.
    """
    lines = [
        "User-agent: *",  # Применяется ко всем ботам (Googlebot, YandexBot и т.д.)
        "Allow: /",       # Разрешаем индексацию всего сайта по умолчанию
        "Disallow: /rws!-cozy-admin/",  # Запрещаем админку (ваш кастомный путь)
        "Disallow: /api/",             # Запрещаем API (не индексируем внутренние данные)
        "Disallow: /cart/",            # Запрещаем корзину (личные данные пользователя)
        "Disallow: /orders/",          # Запрещаем заказы (личная информация)
        "Disallow: /users/",           # Запрещаем личный кабинет (если это профили пользователей)
        "Disallow: /captcha/",         # Запрещаем CAPTCHA (утилитарные страницы)
        "Disallow: /ckeditor5/",
        "Disallow: /rws!-flower-admin/",
        "",                            # Пустая строка для разделителя
        "Sitemap: https://cozy-opt.ru/sitemap.xml"  # Ссылка на вашу sitemap (замените yourdomain.com на реальный домен)
    ]
    content = "\n".join(lines)  # Формируем текст с переносами строк
    return HttpResponse(content, content_type="text/plain")





urlpatterns = [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('rws!-cozy-admin/', admin.site.urls),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('users/', include('users.urls')),
    path('', include('home.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('api/', include('api.urls', namespace='api')),
    path('captcha/', include('captcha.urls')),
    path('robots.txt', robots_txt, name='robots_txt'),
        ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ debug_toolbar_urls()
    