from django.contrib.auth.hashers import check_password
from django.utils.http import urlencode
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.serializers.public_user_authenticating_serializer import (
    PublicUserAuthenticatingSerializer,
)
from main.serializers.public_user_create_serializer import PublicUserCreateSerializer
from main.serializers.public_user_email_verifying_serializer import (
    PublicUserEmailVerifyingSerializer,
)
from main.serializers.public_user_password_resetting_serializer import (
    PublicUserPasswordResettingSerializer,
)
from main.serializers.public_user_update_serializer import PublicUserUpdateSerializer
from main.shortcuts import (
    delete_email_verifying_token,
    get_authentication_token,
    get_email_verifying_token,
    get_password_resetting_token,
    set_authentication_token,
    set_password_resetting_token,
)
from main.view_sets import send_email, send_email_verification


@extend_schema(tags=["public_user"])
class PublicUserViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=("post",))
    def authenticating(self, request, *_args, **_kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            self.queryset, email=serializer.validated_data["email"]
        )
        if not check_password(
            serializer.validated_data["password"], user.hashed_password
        ):
            raise ValidationError("Password is incorrect.")
        if get_authentication_token(user.id) is None:
            set_authentication_token(user.id)
        return Response({
            "user_id": user.id, "token": get_authentication_token(user.id)
        })

    @extend_schema(responses={204: None})
    @action(detail=True, methods=("post",))
    def email_verifying(self, request, *_args, **_kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        token = get_email_verifying_token(user.id)
        if token is None:
            raise ValidationError("Email is already verified.")
        if serializer.validated_data["token"] != token:
            raise ValidationError("Token doesn't match.")
        delete_email_verifying_token(user.id)
        return Response(status=HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        serializer_classes = {
            "authenticating": PublicUserAuthenticatingSerializer,
            "create": PublicUserCreateSerializer,
            "email_verifying": PublicUserEmailVerifyingSerializer,
            "partial_update": PublicUserUpdateSerializer,
            "password_resetting": PublicUserPasswordResettingSerializer,
            "update": PublicUserUpdateSerializer,
        }
        return serializer_classes.get(self.action)

    @extend_schema(responses={204: None})
    @action(detail=False, methods=("post",))
    def password_resetting(self, request, *_arg, **_kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            self.queryset, email=serializer.validated_data["email"]
        )
        if get_email_verifying_token(user.id) is not None:
            raise ValidationError("Email isn't verified.")
        set_password_resetting_token(user.id)
        uri_path = reverse(
            "public-user-password-resetting",
            request=request,
        )
        query = urlencode({"token": get_password_resetting_token(user.id)})
        send_email.delay(
            message=f"{uri_path}?{query}",
            recipient_list=[user.email],
            subject="Konbinein Password Reset",
        )
        return Response(status=HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        user = serializer.save()
        send_email_verification(self.request, user)
