from django.shortcuts import render
from django.utils import timezone
from .models import Visit
from django.db.models import Count
from datetime import timedelta  # Импортируем timedelta

def visit_view(request):
    period = request.GET.get('period', '1_day')
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Определяем начальное время в зависимости от выбранного периода
    if period == '1_day':
        start_time = today_start - timedelta(days=1)
    elif period == '3_days':
        start_time = today_start - timedelta(days=3)
    elif period == '1_week':
        start_time = today_start - timedelta(weeks=1)
    elif period == '1_month':
        start_time = today_start - timedelta(days=30)
    elif period == '1_quarter':
        start_time = today_start - timedelta(days=90)
    elif period == '1_year':
        start_time = today_start - timedelta(days=365)
    else:
        start_time = today_start  # Если период не распознан, берем только сегодня

    # Получаем все посещения за выбранный период
    visits = Visit.objects.filter(visit_time__gte=start_time)

    # Подсчитываем количество посещений
    visit_count = visits.count()

    # Подсчитываем количество уникальных пользователей
    unique_users_count = visits.values('user').distinct().count()

    return render(request, 'admin/visit_user/visits.html', {
        'visit_count': visit_count,
        'unique_users_count': unique_users_count,
        'selected_period': period,
        'visits': visits,  # Передаем посещения для отображения в шаблоне
    })