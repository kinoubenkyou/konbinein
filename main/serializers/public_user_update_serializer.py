from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main import get_password_resetting_token
from main.models.user import User


class PublicUserUpdateSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "password", "token")
        model = User

    password = CharField(max_length=255, write_only=True)
    token = CharField(max_length=255, write_only=True)

    def update(self, instance, validated_data):
        user_attributes = {
            **validated_data,
            "hashed_password": make_password(validated_data["password"]),
        }
        del user_attributes["password"]
        instance = super().update(instance, user_attributes)
        cache.delete(f"password_resetting_token.{instance.id}")
        return instance

    def validate_token(self, value):
        if (
            self.instance is not None
            and get_password_resetting_token(self.instance.id) != value
        ):
            raise ValidationError(detail="Token doesn't match.")
        return value
