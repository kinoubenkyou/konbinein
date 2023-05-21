from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.models.organization import Organization
from main.permissions.user_permission import UserPermission
from main.serializers.organization_serializer import OrganizationSerializer


class UserOrganizationViewSet(ListModelMixin, GenericViewSet):
    ordering_fields = ("code", "id")
    permission_classes = (UserPermission,)
    queryset = Organization.objects.all()
    search_fields = ("code",)
    serializer_class = OrganizationSerializer
