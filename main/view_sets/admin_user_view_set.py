from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.permissions.admin_permission import AdminPermission
from main.serializers.user_serializer import UserSerializer


class AdminUserViewSet(GenericViewSet, ListModelMixin):
    ordering_fields = ("email", "id")
    permission_classes = (AdminPermission,)
    queryset = User.objects.all()
    search_fields = ("email",)
    serializer_class = UserSerializer
