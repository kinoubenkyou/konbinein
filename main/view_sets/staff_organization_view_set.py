from drf_spectacular.utils import extend_schema
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from main.documents.activity import OrganizationActivity
from main.models.organization import Organization
from main.permissions.staff_permission import StaffPermission
from main.serializers.organization_serializer import OrganizationSerializer
from main.view_sets.authenticated_destroy_mixin import AuthenticatedDestroyMixin
from main.view_sets.authenticated_update_mixin import AuthenticatedUpdateMixin


@extend_schema(tags=["organizations_organizations"])
class OrganizationViewSet(
    AuthenticatedDestroyMixin,
    RetrieveModelMixin,
    AuthenticatedUpdateMixin,
    GenericViewSet,
):
    activity_class = OrganizationActivity
    permission_classes = (StaffPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["organization_id"])
