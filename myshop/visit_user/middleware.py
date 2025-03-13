from django.utils import timezone
from .models import Visit
from datetime import timedelta

class VisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Получаем IP-адрес пользователя
        ip_address = request.META.get('REMOTE_ADDR')

        # Определяем, был ли пользователь аутентифицирован
        if request.user.is_authenticated:
            # Сохраняем только для не-администраторов
            if not request.user.is_staff:
                user = request.user
                self.record_visit(user=user, ip_address=ip_address, request=request)
        else:
            # Сохраняем для неавторизованных пользователей
            self.record_visit(user=None, ip_address=ip_address, request=request)

        return response

    def record_visit(self, user, ip_address, request):
        # Проверяем, существует ли запись о визите за последние 24 часа
        now = timezone.now()
        last_24_hours = now - timedelta(days=1)

        # Получаем запись о визите, если она существует
        # Убираем фильтрацию по user для неавторизованных пользователей
        visit = Visit.objects.filter(
            ip_address=ip_address,
            visit_time__gte=last_24_hours
        )

        if user is not None:
            visit = visit.filter(user=user)

        visit = visit.first()

        if visit is None:
            # Если записи нет, создаем новую
            visit = Visit.objects.create(
                user=user,
                ip_address=ip_address,
                referrer=request.META.get('HTTP_REFERER', ''),
                device_type=request.META.get('HTTP_USER_AGENT', ''),
                visit_time=now,
                views_count=1
            )
        else:
            # Если запись уже существует, обновляем ее
            visit.views_count += 1  # Увеличиваем счетчик просмотров
            visit.last_visit = now  # Обновляем время последнего посещения
            visit.save()  # Сохраняем изменения

        # Отладочные сообщения
        print(f"Visit recorded for user: {user}, IP: {ip_address}, Views: {visit.views_count}, Last Visit: {visit.last_visit}")