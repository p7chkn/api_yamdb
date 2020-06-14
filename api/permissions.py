from rest_framework.permissions import BasePermission


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
