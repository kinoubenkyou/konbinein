from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.filter_sets.organization_filter_set import OrganizationFilterSet
from main.models.organization import Organization
from main.permissions.user_permission import UserPermission
from main.serializers.organization_serializer import OrganizationSerializer
from main.view_sets.filter_mixin import FilterMixin


@extend_schema(tags=["users_organizations"])
class UserOrganizationViewSet(FilterMixin, ListModelMixin, GenericViewSet):
    filter_set_class = OrganizationFilterSet
    ordering_fields = ("code", "id")
    permission_classes = (UserPermission,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
