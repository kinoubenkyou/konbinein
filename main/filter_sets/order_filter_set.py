from rest_framework.fields import CharField, DateTimeField, ListField
from rest_framework.serializers import Serializer


class OrderFilterSet(Serializer):
    code__in = ListField(child=CharField(max_length=255))
    created_at__gte = DateTimeField()
    created_at__lte = DateTimeField()
    orderitem__name__in = ListField(child=CharField(max_length=255))
