from django.contrib.auth.hashers import make_password
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.user import User
from main.shortcuts import set_email_verifying_token


class PublicUserCreateSerializer(ModelSerializer):
    class Meta:
        fields = ("email", "id", "name", "password")
        model = User

    password = CharField(max_length=255, write_only=True)

    def create(self, validated_data):
        user_attributes = {
            **validated_data,
            "hashed_password": make_password(validated_data["password"]),
            "is_system_administrator": False,
        }
        del user_attributes["password"]
        instance = super().create(user_attributes)
        set_email_verifying_token(instance.id)
        return instance
