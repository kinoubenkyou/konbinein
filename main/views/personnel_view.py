from django.db import transaction
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
from main.permissions.user_permission import UserPermission
from main.serializers.personnel_serializer import PersonnelSerializer


class PersonnelViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("does_organization_agree", "does_user_agree")
    permission_classes = (UserPermission,)
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user.id)

    @action(detail=True, methods=("post",))
    @transaction.atomic()
    def agreeing(self, request, *args, **kwargs):
        personnel = self.get_object()
        personnel.does_user_agree = True
        personnel.save()
        return Response(status=HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        request.data["does_organization_agree"] = False
        request.data["does_user_agree"] = True
        request.data["user"] = request.user.id
        return super().create(request, *args, **kwargs)
