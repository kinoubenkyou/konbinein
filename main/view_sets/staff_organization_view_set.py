from drf_spectacular.utils import extend_schema
from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from main.models.organization import Organization
from main.permissions.staff_permission import StaffPermission
from main.serializers.organization_serializer import OrganizationSerializer


@extend_schema(tags=["organizations_organizations"])
class OrganizationViewSet(
    DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    permission_classes = (StaffPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["organization_id"])
