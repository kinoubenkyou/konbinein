from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import GenericViewSet

from main.documents.organization_activity import OrganizationActivity
from main.models.organization import Organization
from main.permissions.admin_permission import AdminPermission
from main.serializers.admin_organization_serializer import AdminOrganizationSerializer
from main.shortcuts import ActivityType
from main.view_sets.create_mixin import CreateMixin


@extend_schema(tags=["admin_organizations"])
class AdminOrganizationViewSet(CreateMixin, GenericViewSet):
    activity_class = OrganizationActivity
    activity_type = ActivityType.ADMIN
    permission_classes = (AdminPermission,)
    queryset = Organization.objects.all()
    serializer_class = AdminOrganizationSerializer
