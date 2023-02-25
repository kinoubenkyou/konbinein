from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from main.models.user import User
from main.permissions.user_permission import UserPermission
from main.serializers.user_serializer import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        permission_dict = {
            "authenticating": (),
            "create": (),
            "email_verifying": (),
        }
        permission_classes = permission_dict.get(self.action, (UserPermission,))
        return (permission_class() for permission_class in permission_classes)

    @action(detail=False, methods=("post",))
    @transaction.atomic
    def authenticating(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = get_object_or_404(self.queryset, email=email)
        password = request.data.get("password")
        if not check_password(password, user.hashed_password):
            return Response(
                data={"detail": "Password is incorrect."}, status=HTTP_400_BAD_REQUEST
            )
        if user.authentication_token is None:
            user.authentication_token = Token.generate_key()
            user.save()
        return Response({"token": user.authentication_token})

    @action(detail=False, methods=("post",))
    @transaction.atomic
    def de_authenticating(self, request, *args, **kwargs):
        request.user.authentication_token = None
        request.user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=("post",))
    @transaction.atomic
    def email_verifying(self, request, *args, **kwargs):
        user = self.get_object()
        token = user.email_verification_token
        if token is None:
            return Response(
                data={"detail": "Email is already verified."},
                status=HTTP_400_BAD_REQUEST,
            )
        if request.data.get("token") != token:
            return Response(
                data={"detail": "Token doesn't match."}, status=HTTP_400_BAD_REQUEST
            )
        user.email_verification_token = None
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=("post",))
    @transaction.atomic
    def password_resetting(self, request, *args, **kwargs):
        user = self.get_object()
        if user.email_verification_token is not None:
            return Response(
                data={"detail": "Email isn't verified."}, status=HTTP_400_BAD_REQUEST
            )
        password = Token.generate_key()
        user.hashed_password = make_password(password)
        user.save()
        send_mail(
            from_email=None,
            message=f"{password}",
            recipient_list=(user.email,),
            subject="Konbinein Password Resetting",
        )
        return Response(status=HTTP_204_NO_CONTENT)
