from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.models.organization import Organization
from main.permissions.user_permission import UserPermission
from main.serializers.organization_serializer import OrganizationSerializer


class UserOrganizationViewSet(GenericViewSet, ListModelMixin):
    permission_classes = (UserPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
