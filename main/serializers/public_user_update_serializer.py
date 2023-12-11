from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.user import User
from main.shortcuts import delete_password_resetting_token, get_password_resetting_token


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
        delete_password_resetting_token(instance.id)
        return instance

    def validate_token(self, value):
        if (
            self.instance is not None
            and get_password_resetting_token(self.instance.id) != value
        ):
            raise ValidationError(detail="Token doesn't match.")
        return value
