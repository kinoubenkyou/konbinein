from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils.http import urlencode
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

from main.models.user import User


class UserSerializer(ModelSerializer):
    password = CharField(max_length=255, write_only=True)
    current_password = CharField(max_length=255, required=False, write_only=True)

    class Meta:
        fields = ["email", "id", "name", "password", "current_password"]
        model = User

    @staticmethod
    def _modify_to_attributes(validated_data):
        if "current_password" in validated_data:
            del validated_data["current_password"]
        if "email" in validated_data:
            validated_data["email_verification_token"] = Token.generate_key()
        if "password" in validated_data:
            password = validated_data.pop("password")
            validated_data["hashed_password"] = make_password(password)

    def _send_email_verification(self, user):
        if user.email_verification_token is not None:
            uri_path = reverse(
                "user-email-verifying",
                kwargs={"pk": user.id},
                request=self.context["request"],
            )
            query = urlencode({"token": user.email_verification_token})
            send_mail(
                from_email=None,
                message=f"{uri_path}?{query}",
                recipient_list=(user.email,),
                subject="Konbinein Email Verification",
            )

    @transaction.atomic
    def create(self, validated_data):
        self._modify_to_attributes(validated_data)
        user = super().create(validated_data)
        self._send_email_verification(user)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        self._modify_to_attributes(validated_data)
        user = super().update(instance, validated_data)
        self._send_email_verification(user)
        return instance

    def validate(self, attrs):
        if self.instance is not None and ("password" in attrs or "email" in attrs):
            if "current_password" not in attrs:
                raise ValidationError(
                    code="current_password_required",
                    detail="Current password is required.",
                )
            if not check_password(
                attrs["current_password"], self.instance.hashed_password
            ):
                raise ValidationError(
                    code="current_password_incorrect",
                    detail="Current password is incorrect.",
                )
        return attrs
