from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None and request.user.is_system_administrator
