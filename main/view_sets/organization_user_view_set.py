from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.filter_sets.user_filter_set import UserFilterSet
from main.models.user import User
from main.permissions.staff_permission import StaffPermission
from main.serializers.user_serializer import UserSerializer


@extend_schema(tags=["organizations_users"])
class OrganizationUserViewSet(ListModelMixin, GenericViewSet):
    filter_set_class = UserFilterSet
    ordering_fields = ("email", "id", "name")
    permission_classes = (StaffPermission,)
    queryset = User.objects.all()
    serializer_class = UserSerializer