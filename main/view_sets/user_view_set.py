from rest_framework.decorators import action
from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.permissions.user_permission import UserPermission
from main.serializers.user_serializer import UserSerializer
from main.view_sets import send_email_verification


class UserViewSet(
    DestroyModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet
):
    permission_classes = (UserPermission,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["user_id"])

    @action(detail=True, methods=("post",))
    def de_authenticating(self, request, *args, **kwargs):
        user = self.get_object()
        user.authentication_token = None
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        current_email = serializer.instance.email
        user = serializer.save()
        if current_email != user.email:
            send_email_verification(self.request, user)
