from rest_framework.fields import CharField, EmailField, IntegerField
from rest_framework.serializers import Serializer


class PublicUserAuthenticatingSerializer(Serializer):
    email = EmailField(write_only=True)
    password = CharField(max_length=255, write_only=True)
    user_id = IntegerField(read_only=True)
    token = CharField(max_length=255, read_only=True)
