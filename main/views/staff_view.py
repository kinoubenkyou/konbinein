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

from main.models.staff import Staff
from main.permissions.user_permission import UserPermission
from main.serializers.staff_serializer import StaffSerializer


class StaffViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
):
    permission_classes = (UserPermission,)
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user.id)

    @action(detail=True, methods=("post",))
    def agreeing(self, request, *args, **kwargs):
        staff = self.get_object()
        staff.does_user_agree = True
        staff.save()
        return Response(status=HTTP_204_NO_CONTENT)
