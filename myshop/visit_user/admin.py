from django.contrib import admin
from .models import Visit

class VisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'referrer', 'visit_time')
    list_filter = ('user', 'visit_time')


admin.site.register(Visit, VisitAdmin)