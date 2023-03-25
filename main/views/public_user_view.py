from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from main.models.user import User
from main.serializers.public_user_serializer import PublicUserSerializer
from main.views.user_view_mixin import UserViewSetMixin


class PublicUserViewSet(CreateModelMixin, GenericViewSet, UserViewSetMixin):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer

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
        token = user.email_verification_token
        if token is None:
            raise ValidationError("Email is already verified.")
        if request.data.get("token") != token:
            raise ValidationError("Token doesn't match.")
        user.email_verification_token = None
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=("post",))
    def password_resetting(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = get_object_or_404(self.queryset, email=email)
        if user.email_verification_token is not None:
            raise ValidationError("Email isn't verified.")
        password = Token.generate_key()
        user.hashed_password = make_password(password)
        user.save()
        send_mail(
            from_email=None,
            message=password,
            recipient_list=(user.email,),
            subject="Konbinein Password Reset",
        )
        return Response(status=HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_email_verification(self.request, user)
