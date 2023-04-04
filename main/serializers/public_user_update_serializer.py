from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.user import User


class PublicUserUpdateSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "password", "token")
        model = User

    password = CharField(max_length=255, write_only=True)
    token = CharField(max_length=255, write_only=True)

    def update(self, instance, validated_data):
        user_attributes = validated_data | {
            "hashed_password": make_password(validated_data["password"]),
            "password_resetting_token": None,
        }
        del user_attributes["password"]
        return super().update(instance, user_attributes)

    def validate_token(self, value):
        if (
            self.instance is not None
            and self.instance.password_resetting_token != value
        ):
            raise ValidationError(detail="Token doesn't match.")
        return value
