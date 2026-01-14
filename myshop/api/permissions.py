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




# class OrderPermission(BasePermission):
#     """
#     Админы: CRUD для всех заказов.
#     Аутентифицированные: Только просмотр своих заказов (по email).
#     """
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated

#     def has_object_permission(self, request, view, obj):
#         user = request.user
#         if user.is_staff:
#             return True
#         return obj.email == user.email  # Только свои заказы




# class OrderPermission(BasePermission):
#     """
#     Админы: полный доступ ко всем заказам.
#     Сборщики (is_picker=True): доступ ко всем заказам со статусом 'obrabotka'.
#     Остальные: только свои заказы (по email).
#     """

#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated)

#     def has_object_permission(self, request, view, obj):
#         user = request.user

#         # Админ – всё
#         if user.is_staff:
#             return True

#         # Сборщик – все заказы только со статусом 'obrabotka'
#         if getattr(user, 'is_picker', False):
#             return obj.status == 'obrabotka'

#         # Обычный пользователь – только свои заказы
#         return obj.email == user.email





class OrderPermission(BasePermission):
    """
    Админы: полный доступ ко всем заказам.
    Сборщики (is_picker=True):
        - видят заказы со статусом 'obrabotka',
        - и (если нужно) только те, где assigned_to = user.
    Остальные: только свои заказы (по email).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Админ – всё
        if user.is_staff:
            return True

        # Сборщик – заказы в обработке, назначенные ему
        if getattr(user, 'is_picker', False):
            # если хочешь только 'obrabotka'
            if obj.status != 'obrabotka':
                return False
            # если хочешь, чтобы видел только свои назначенные
            if obj.assigned_to_id is not None and obj.assigned_to_id != user.id:
                return False
            return True

        # Обычный пользователь – только свои заказы по email
        return obj.email == user.email


