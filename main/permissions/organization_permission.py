from rest_framework.permissions import BasePermission

from main.models.personnel import Personnel


class OrganizationPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user is not None
            and Personnel.objects.filter(
                does_organization_agree=True,
                does_user_agree=True,
                organization=view.kwargs["organization_id"],
                user=request.user.id,
            ).exists()
        )

    def has_object_permission(self, request, view, obj):
        return str(obj.organization_id) == view.kwargs["organization_id"]
