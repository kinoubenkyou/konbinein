from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from main.models.organization import Organization
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.organization_serializer import OrganizationSerializer


class OrganizationViewSet(
    DestroyModelMixin, GenericViewSet, RetrieveModelMixin, UpdateModelMixin
):
    permission_classes = (OrganizationPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_url_kwarg = "organization_id"
