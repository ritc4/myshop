from django.utils import timezone
from .models import Visit

class VisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Сохраните информацию о визите
        if request.user.is_authenticated:
            # Сохраняем только для не-администраторов
            if not request.user.is_staff:
                user = request.user
                Visit.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    referrer=request.META.get('HTTP_REFERER', ''),
                    visit_time=timezone.now(),
                    device_type=request.META.get('HTTP_USER_AGENT', '')
                )
        else:
            # Сохраняем для неавторизованных пользователей
            Visit.objects.create(
                user=None,  # Указываем, что пользователь не авторизован
                ip_address=request.META.get('REMOTE_ADDR'),
                referrer=request.META.get('HTTP_REFERER', ''),
                visit_time=timezone.now(),
                device_type=request.META.get('HTTP_USER_AGENT', '')
            )

        return response
