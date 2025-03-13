from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Visit
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg



# @admin.register(Visit)
# class VisitAdmin(admin.ModelAdmin):
#     list_display = ('user', 'ip_address', 'referrer', 'visit_time')
#     list_filter = ('user', 'visit_time')



@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'referrer', 'visit_time')
    list_filter = ('user', 'visit_time')

    change_list_template = "admin/visit_user/visits.html"  # Укажите свой шаблон

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.visit_view), name='visit'),
        ]
        return custom_urls + urls

    
    def visit_view(self, request):
        # Получаем период из GET-запроса, по умолчанию '1_day'
        period = request.GET.get('period', '1_day')
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Определяем начальное время в зависимости от выбранного периода
        period_mapping = {
            '1_day': timedelta(days=1),
            '3_days': timedelta(days=3),
            '1_week': timedelta(weeks=1),
            '1_month': timedelta(days=30),
            '1_quarter': timedelta(days=90),
            '1_year': timedelta(days=365),
        }

        # Устанавливаем начальное время
        start_time = today_start - period_mapping.get(period, timedelta(days=1))  # Установим по умолчанию 1 день

        # Получаем все посещения за выбранный период
        visits = Visit.objects.filter(visit_time__gte=start_time)

        # Подсчитываем общее количество посещений
        visit_count = visits.values('id').count()
        print(visit_count)

        # Подсчитываем общее количество просмотров
        total_views = sum(visits.values_list('views_count', flat=True))
        print(total_views)


        if visit_count > 0:
            average_depth_of_view = total_views / visit_count
        else:
            average_depth_of_view = 0

        print(average_depth_of_view)


        # Примерные данные для других метрик
        total_orders = 2  # Здесь можно добавить логику для вычисления
        successful_orders = 2  # Здесь можно добавить логику для вычисления
        conversion_rate = (successful_orders / total_orders * 100) if total_orders > 0 else 0
        average_check = 6135  # Здесь можно добавить логику для вычисления
        turnover = total_orders * average_check  # Оборот

        # Сбор данных для графика
        visits_counts = visits.values('visit_time').annotate(total_visits=Count('id')).order_by('visit_time')

        # Преобразуем данные для графика
        visit_dates = [visit['visit_time'].strftime('%Y-%m-%d') for visit in visits_counts]
        visit_numbers = [visit['total_visits'] for visit in visits_counts]


        # Подсчет уникальных пользователей и средней глубины просмотров по источникам
        visits_by_referrer = (
            visits.values('referrer').annotate(
                user_count=Count('id', distinct=True),  # Подсчет уникальных пользователей
                average_view_refferer=Avg('views_count'),  # Подсчет средней глубины просмотров
            )
            .order_by('-user_count')  # Сортировка по количеству уникальных пользователей
            )

        print([i['average_view_refferer'] / i['user_count'] for i in visits_by_referrer])

        # Обработка случая, если referrer не задан
        for i in visits_by_referrer:
            if not i['referrer']:
                i['referrer'] = 'Источник не определён'

            if i['user_count'] > 0:
                i['view_refferer'] = i['average_view_refferer'] / i['user_count']  # Средняя глубина просмотров на пользователя
            else:
                i['view_refferer'] = 0

        print(visits_by_referrer)

        return render(request, 'admin/visit_user/visits.html', {
            'visit_count': visit_count,
            'total_views': total_views,
            'selected_period': period,
            'visits': visits,
            'average_depth_of_view': average_depth_of_view,
            'total_orders': total_orders,
            'successful_orders': successful_orders,
            'conversion_rate': conversion_rate,
            'average_check': average_check,
            'turnover': turnover,
            'visits_counts': visits_counts,
            'visit_dates': visit_dates,
            'visit_numbers': visit_numbers,
            'visits_by_referrer': visits_by_referrer,  # Передаем данные о пользователях по источникам
            })



