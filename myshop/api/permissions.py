# api/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminOrAuthenticatedReadOnly(BasePermission):
    """
    Админы: CRUD.
    Аутентифицированные (не админы): Только чтение (GET).
    """
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                return True  # Админы: полный доступ
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True  # Аутентифицированные: только чтение
        return False  # Анонимы: нет доступа

class OrderPermission(BasePermission):
    """
    Админы: CRUD для всех заказов.
    Аутентифицированные: Только просмотр своих заказов (по email).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True
        return obj.email == user.email  # Только свои заказы
