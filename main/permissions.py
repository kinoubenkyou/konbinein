from rest_framework.permissions import BasePermission


class AuthenticatedPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None


class UserPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
