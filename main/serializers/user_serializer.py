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
    current_password = CharField(max_length=255, required=False, write_only=True)
    password = CharField(max_length=255, write_only=True)

    class Meta:
        fields = [
            "current_password",
            "email",
            "id",
            "name",
            "password",
        ]
        model = User

    @property
    def _current_password_required_error(self):
        return ValidationError(
            code="current_password_required",
            detail="Current password is required.",
        )

    def _send_email_verification(self, user):
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
        user_attributes = validated_data | {
            "email_verification_token": Token.generate_key(),
            "hashed_password": make_password(validated_data["password"]),
            "is_system_administrator": False,
        }
        del user_attributes["password"]
        user = super().create(user_attributes)
        self._send_email_verification(user)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        is_email_updated = False
        user_attributes = validated_data | {"is_system_administrator": False}
        if "email" in user_attributes and user_attributes["email"] != instance.email:
            user_attributes["email_verification_token"] = Token.generate_key()
            is_email_updated = True
        if "password" in user_attributes and not check_password(
            validated_data["password"], instance.hashed_password
        ):
            user_attributes["hashed_password"] = make_password(
                validated_data["password"]
            )
            user_attributes.pop("password")
        user = super().update(instance, user_attributes)
        if is_email_updated:
            self._send_email_verification(user)
        return user

    def validate_email(self, value):
        if (
            self.instance is not None
            and self.instance.email != value
            and "current_password" not in self.initial_data
        ):
            raise self._current_password_required_error
        return value

    def validate_password(self, value):
        if (
            self.instance is not None
            and not check_password(value, self.instance.hashed_password)
            and "current_password" not in self.initial_data
        ):
            raise self._current_password_required_error
        return value

    def validate_current_password(self, value):
        if not check_password(value, self.instance.hashed_password):
            raise ValidationError(
                code="current_password_incorrect",
                detail="Current password is incorrect.",
            )
        return value
