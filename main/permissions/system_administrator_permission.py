from rest_framework.permissions import BasePermission


class SystemAdministratorPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_system_administrator
