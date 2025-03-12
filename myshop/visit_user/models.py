from django.conf import settings
from django.db import models

class Visit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    referrer = models.URLField(null=True, blank=True)
    visit_time = models.DateTimeField(auto_now_add=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.user} visited on {self.visit_time} from {self.ip_address}'

    def get_visit_info(self):
        return {
            'user': self.user.username if self.user else 'Anonymous',
            'ip_address': self.ip_address,
            'referrer': self.referrer,
            'visit_time': self.visit_time,
            'device_type': self.device_type,
        }