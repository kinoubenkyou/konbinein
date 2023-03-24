from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from main.models.organization import Organization
from main.permissions.admin_permission import AdminPermission
from main.serializers.admin_organization_serializer import AdminOrganizationSerializer


class AdminOrganizationViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (AdminPermission,)
    queryset = Organization.objects.all()
    serializer_class = AdminOrganizationSerializer
