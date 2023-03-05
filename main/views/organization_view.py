from rest_framework.viewsets import ModelViewSet

from main.models.organization import Organization
from main.permissions.system_administrator_permission import (
    SystemAdministratorPermission,
)
from main.serializers.organization_serializer import OrganizationSerializer


class OrganizationViewSet(ModelViewSet):
    permission_classes = (SystemAdministratorPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
