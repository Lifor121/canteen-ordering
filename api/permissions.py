from rest_framework.permissions import BasePermission

class IsCanteenWorker(BasePermission):
    message = 'Доступ разрешен только для сотрудников столовой.'

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == 'worker' and user.canteen is not None