from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Указываем поля, которые будут отображаться в списке пользователей
    list_display = ('id', 'username', 'email', 'first_name', 'phone', 'region', 'city', 'delivery_method', 'is_picker')

    # # Указываем поля, которые будут доступны для редактирования
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone', 'region', 'city', 'address', 'postal_code', 'delivery_method')}),
    # )

    fieldsets = ((None, {'fields': ('username', 'password'),}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'email','phone', 'region', 'city', 'address','postal_code', 'photo', 'delivery_method',),}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser','is_picker','groups', 'user_permissions',),}),
        ('Важные даты', {'fields': ('last_login', 'date_joined'),}),
    )

    # Указываем поля для фильтрации в админке
    list_filter = UserAdmin.list_filter + ('delivery_method', 'is_picker')

    # Указываем поля для поиска
    search_fields = UserAdmin.search_fields + ('phone', 'region', 'city', 'is_picker')


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('delivery_method') 