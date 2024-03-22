from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.documents.activity import UserStaffActivity
from main.filter_sets.staff_filter_set import StaffFilterSet
from main.models.staff import Staff
from main.permissions.user_permission import UserPermission
from main.serializers.user_staff_serializer import UserStaffSerializer
from main.view_sets.authenticated_create_mixin import AuthenticatedCreateMixin


@extend_schema(tags=["users_staffs"])
class UserStaffViewSet(
    AuthenticatedCreateMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    activity_class = UserStaffActivity
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

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=("post",))
    def agreeing(self, request, *args, **kwargs):
        staff = self.get_object()
        staff.does_user_agree = True
        staff.save()
        return Response(status=HTTP_204_NO_CONTENT)
