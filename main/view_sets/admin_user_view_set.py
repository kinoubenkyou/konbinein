from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.filter_sets.user_filter_set import UserFilterSet
from main.models.user import User
from main.permissions.admin_permission import AdminPermission
from main.serializers.user_serializer import UserSerializer
from main.view_sets.filter_mixin import FilterMixin


class AdminUserViewSet(FilterMixin, ListModelMixin, GenericViewSet):
    filter_set_class = UserFilterSet
    ordering_fields = ("email", "id")
    permission_classes = (AdminPermission,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
