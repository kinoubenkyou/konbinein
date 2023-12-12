from rest_framework.fields import EmailField
from rest_framework.serializers import Serializer


class PublicUserPasswordResettingSerializer(Serializer):
    email = EmailField(write_only=True)
