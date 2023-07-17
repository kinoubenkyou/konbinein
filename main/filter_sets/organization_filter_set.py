from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class OrganizationFilterSet(Serializer):
    code__icontains = CharField(max_length=255)
    name__icontains = CharField(max_length=255)
