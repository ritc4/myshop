from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Указываем поля, которые будут отображаться в списке пользователей
    list_display = ('username', 'email', 'first_name', 'phone', 'region', 'city', 'delivery_method')

    # Указываем поля, которые будут доступны для редактирования
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'region', 'city', 'address', 'postal_code', 'delivery_method')}),
    )

    # Указываем поля для фильтрации в админке
    list_filter = UserAdmin.list_filter + ('delivery_method',)

    # Указываем поля для поиска
    search_fields = UserAdmin.search_fields + ('phone', 'region', 'city')


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('delivery_method') 