from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.role == 'AD'
        except Exception:
            return False
