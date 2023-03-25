from rest_framework.permissions import BasePermission

from main.models.staff import Staff


class StaffPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user is not None
            and Staff.objects.filter(
                does_organization_agree=True,
                does_user_agree=True,
                organization=view.kwargs["organization_id"],
                user=request.user.id,
            ).exists()
        )
