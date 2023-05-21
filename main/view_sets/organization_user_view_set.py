from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.permissions.staff_permission import StaffPermission
from main.serializers.user_serializer import UserSerializer


class OrganizationUserViewSet(ListModelMixin, GenericViewSet):
    ordering_fields = ("email", "id")
    permission_classes = (StaffPermission,)
    queryset = User.objects.all()
    search_fields = ("email",)
    serializer_class = UserSerializer
