from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class PublicUserEmailVerifyingSerializer(Serializer):
    token = CharField(max_length=255, write_only=True)
