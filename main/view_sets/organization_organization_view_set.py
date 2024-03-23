from drf_spectacular.utils import extend_schema
from rest_framework.mixins import DestroyModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from main.documents.organization_activity import OrganizationActivity
from main.models.organization import Organization
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.organization_serializer import OrganizationSerializer
from main.shortcuts import ActivityType
from main.view_sets.update_mixin import UpdateMixin


@extend_schema(tags=["organizations_organizations"])
class OrganizationOrganizationViewSet(
    UpdateMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    activity_class = OrganizationActivity
    activity_type = ActivityType.ORGANIZATION
    permission_classes = (OrganizationPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["organization_id"])
