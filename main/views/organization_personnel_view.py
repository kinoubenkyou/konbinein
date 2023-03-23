from django_filters.rest_framework import DjangoFilterBackend
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

from main.models.personnel import Personnel
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.organization_personnel_serializer import (
    OrganizationPersonnelSerializer,
)


class OrganizationPersonnelViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("does_user_agree", "user")
    permission_classes = (OrganizationPermission,)
    queryset = Personnel.objects.all()
    serializer_class = OrganizationPersonnelSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )

    @action(detail=True, methods=("post",))
    def agreeing(self, request, *args, **kwargs):
        personnel = self.get_object()
        personnel.does_organization_agree = True
        personnel.save()
        return Response(status=HTTP_204_NO_CONTENT)
