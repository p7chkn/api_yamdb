from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            if view.kwargs['username'] == 'me' and request.user.role:
                return True
        except Exception:
            pass

        try:
            return request.user.role == 'admin'
        except Exception:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        try:
            return request.user.role == 'admin'
        except Exception:
            return False
