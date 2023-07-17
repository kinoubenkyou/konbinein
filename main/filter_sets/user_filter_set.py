from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class UserFilterSet(Serializer):
    email__icontains = CharField(max_length=255)
    name__icontains = CharField(max_length=255)
