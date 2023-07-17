from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.filter_sets.staff_filter_set import StaffFilterSet
from main.models.staff import Staff
from main.permissions.user_permission import UserPermission
from main.serializers.user_staff_serializer import UserStaffSerializer
from main.view_sets.filter_mixin import FilterMixin


class UserStaffViewSet(
    FilterMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
):
    filter_set_class = StaffFilterSet
    ordering_fields = (
        "does_organization_agree",
        "does_user_agree",
        "id",
        "organization__code",
    )
    permission_classes = (UserPermission,)
    queryset = Staff.objects.all()
    serializer_class = UserStaffSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user.id)

    @action(detail=True, methods=("post",))
    def agreeing(self, request, *args, **kwargs):
        staff = self.get_object()
        staff.does_user_agree = True
        staff.save()
        return Response(status=HTTP_204_NO_CONTENT)
