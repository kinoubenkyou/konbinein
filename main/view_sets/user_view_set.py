from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.documents.activity import UserActivity
from main.models.user import User
from main.permissions.user_permission import UserPermission
from main.serializers.user_serializer import UserSerializer
from main.shortcuts import delete_authentication_token
from main.view_sets import send_email_verification
from main.view_sets.authenticated_destroy_mixin import AuthenticatedDestroyMixin
from main.view_sets.authenticated_update_mixin import AuthenticatedUpdateMixin


@extend_schema(tags=["users_users"])
class UserViewSet(
    AuthenticatedDestroyMixin,
    AuthenticatedUpdateMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    activity_class = UserActivity
    permission_classes = (UserPermission,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["user_id"])

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=("post",))
    def de_authenticating(self, _request, *_args, **_kwargs):
        user = self.get_object()
        delete_authentication_token(user.id)
        return Response(status=HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        current_email = serializer.instance.email
        super().perform_update(serializer)
        user = serializer.instance
        if current_email != user.email:
            send_email_verification(self.request, user)
