from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework import permissions, exceptions


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            if view.kwargs["username"] == "me" and request.user.role:
                return True
        except Exception:
            pass

        try:
            return request.user.role == "admin"
        except Exception:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        try:
            return request.user.role == "admin"
        except Exception:
            return False


class  MethodPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.kwargs:
            if request.method == 'DELETE':
                return True
            raise exceptions.MethodNotAllowed(request.method)
        return True
