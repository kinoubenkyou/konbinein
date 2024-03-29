from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user is not None and str(request.user.id) == view.kwargs["user_id"]
        )
