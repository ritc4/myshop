from django.conf import settings
from django.db import models

class Visit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    referrer = models.URLField(null=True, blank=True)
    visit_time = models.DateTimeField(auto_now_add=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    views_count = models.PositiveIntegerField(default=1)  # Счетчик просмотров
    last_visit = models.DateTimeField(auto_now=True)  # Дата последнего посещения

    def __str__(self):
        return f'{self.user} visited on {self.visit_time} from {self.ip_address},{self.views_count}'
    
    class Meta:
        verbose_name = 'Визит пользователя'
        verbose_name_plural = 'Визиты пользователей'
