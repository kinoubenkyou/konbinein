from rest_framework.permissions import BasePermission

from main.models import Personnel


class AuthenticatedPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None


class OrganizationPermission(BasePermission):
    def has_permission(self, request, view):
        return Personnel.objects.filter(
            does_organization_agree=True,
            does_user_agree=True,
            organization=view.kwargs["organization_id"],
            user=request.user.id,
        ).exists()
