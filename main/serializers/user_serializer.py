from django.contrib.auth.hashers import check_password, make_password
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.user import User


class UserSerializer(ModelSerializer):
    class Meta:
        fields = (
            "current_password",
            "email",
            "id",
            "name",
            "password",
        )
        model = User

    current_password = CharField(max_length=255, required=False, write_only=True)
    password = CharField(max_length=255, write_only=True)

    def update(self, instance, validated_data):
        user_attributes = {**validated_data}
        if "email" in user_attributes and user_attributes["email"] != instance.email:
            user_attributes["email_verifying_token"] = Token.generate_key()
        if "password" in user_attributes and not check_password(
            validated_data["password"], instance.hashed_password
        ):
            user_attributes["hashed_password"] = make_password(
                validated_data["password"]
            )
            user_attributes.pop("password")
        return super().update(instance, user_attributes)

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
            raise ValidationError(detail="Current password is incorrect.")
        return value

    @property
    def _current_password_required_error(self):
        return ValidationError(detail="Current password is required.")
