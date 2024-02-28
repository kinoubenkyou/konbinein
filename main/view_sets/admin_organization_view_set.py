from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import GenericViewSet

from main.documents.activity import AdminOrganizationActivity
from main.models.organization import Organization
from main.permissions.admin_permission import AdminPermission
from main.serializers.admin_organization_serializer import AdminOrganizationSerializer
from main.view_sets.user_create_mixin import UserCreateMixin


@extend_schema(tags=["admin_organizations"])
class AdminOrganizationViewSet(UserCreateMixin, GenericViewSet):
    activity_class = AdminOrganizationActivity
    permission_classes = (AdminPermission,)
    queryset = Organization.objects.all()
    serializer_class = AdminOrganizationSerializer
