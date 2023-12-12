from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.filter_sets.user_filter_set import UserFilterSet
from main.models.user import User
from main.permissions.admin_permission import AdminPermission
from main.serializers.user_serializer import UserSerializer
from main.view_sets.filter_mixin import FilterMixin


@extend_schema(tags=["admin_users"])
class AdminUserViewSet(FilterMixin, ListModelMixin, GenericViewSet):
    filter_set_class = UserFilterSet
    ordering_fields = ("email", "id", "name")
    permission_classes = (AdminPermission,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
