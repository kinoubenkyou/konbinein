from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.user import User


class PublicUserSerializer(ModelSerializer):
    password = CharField(max_length=255, write_only=True)

    class Meta:
        fields = ("email", "id", "name", "password")
        model = User

    def create(self, validated_data):
        user_attributes = validated_data | {
            "email_verifying_token": Token.generate_key(),
            "hashed_password": make_password(validated_data["password"]),
            "is_system_administrator": False,
        }
        del user_attributes["password"]
        return super().create(user_attributes)
