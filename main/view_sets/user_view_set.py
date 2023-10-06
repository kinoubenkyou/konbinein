from rest_framework.decorators import action
from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.permissions.user_permission import UserPermission
from main.serializers.user_serializer import UserSerializer
from main.view_sets import send_email_verification


class UserViewSet(
    DestroyModelMixin, GenericViewSet, UpdateModelMixin, RetrieveModelMixin
):
    lookup_url_kwarg = "user_id"
    permission_classes = (UserPermission,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=("post",))
    def de_authenticating(self, request, *args, **kwargs):
        user = self.get_object()
        user.authentication_token = None
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        current_email = serializer.instance.email
        user = serializer.save()
        uri_path = reverse(
            "public-user-email-verifying",
            kwargs={"pk": user.id},
            request=self.request,
        )
        if current_email != user.email:
            send_email_verification.delay(
                user.email, user.email_verifying_token, uri_path
            )
