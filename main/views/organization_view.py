from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from main.models.organization import Organization
from main.permissions.staff_permission import StaffPermission
from main.serializers.organization_serializer import OrganizationSerializer


class OrganizationViewSet(
    DestroyModelMixin, GenericViewSet, RetrieveModelMixin, UpdateModelMixin
):
    permission_classes = (StaffPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_url_kwarg = "organization_id"
