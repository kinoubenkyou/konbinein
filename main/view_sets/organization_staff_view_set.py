from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.documents.staff_activity import StaffActivity
from main.filter_sets.staff_filter_set import StaffFilterSet
from main.models.staff import Staff
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.staff_serializer import StaffSerializer
from main.shortcuts import ActivityType
from main.view_sets.create_mixin import CreateMixin


@extend_schema(tags=["organizations_staffs"])
class OrganizationStaffViewSet(
    CreateMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    activity_class = StaffActivity
    activity_type = ActivityType.ORGANIZATION
    filter_set_class = StaffFilterSet
    ordering_fields = (
        "does_organization_agree",
        "does_user_agree",
        "id",
        "user__email",
    )
    permission_classes = (OrganizationPermission,)
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=("post",))
    def agreeing(self, request, *args, **kwargs):
        staff = self.get_object()
        staff.does_organization_agree = True
        staff.save()
        return Response(status=HTTP_204_NO_CONTENT)
