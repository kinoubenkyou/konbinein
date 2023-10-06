from django.contrib.auth.hashers import check_password
from django.utils.http import urlencode
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.serializers.public_user_create_serializer import PublicUserCreateSerializer
from main.serializers.public_user_update_serializer import PublicUserUpdateSerializer
from main.view_sets import send_email, send_email_verification


class PublicUserViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=("post",))
    def authenticating(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = get_object_or_404(self.queryset, email=email)
        password = request.data.get("password")
        if not check_password(password, user.hashed_password):
            raise ValidationError("Password is incorrect.")
        if user.authentication_token is None:
            user.authentication_token = Token.generate_key()
            user.save()
        return Response({"token": user.authentication_token})

    @action(detail=True, methods=("post",))
    def email_verifying(self, request, *args, **kwargs):
        user = self.get_object()
        token = user.email_verifying_token
        if token is None:
            raise ValidationError("Email is already verified.")
        if request.data.get("token") != token:
            raise ValidationError("Token doesn't match.")
        user.email_verifying_token = None
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        serializer_classes = {
            "create": PublicUserCreateSerializer,
            "partial_update": PublicUserUpdateSerializer,
        }
        return serializer_classes.get(self.action)

    @action(detail=False, methods=("post",))
    def password_resetting(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = get_object_or_404(self.queryset, email=email)
        if user.email_verifying_token is not None:
            raise ValidationError("Email isn't verified.")
        user.password_resetting_token = Token.generate_key()
        user.save()
        uri_path = reverse(
            "public-user-password-resetting",
            request=request,
        )
        query = urlencode({"token": user.password_resetting_token})
        send_email.delay(
            message=f"{uri_path}?{query}",
            recipient_list=[user.email],
            subject="Konbinein Password Reset",
        )
        return Response(status=HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        user = serializer.save()
        send_email_verification(self.request, user)
