from rest_framework.fields import CharField, DecimalField, ListField
from rest_framework.serializers import Serializer


class ProductFilterSet(Serializer):
    code__in = ListField(child=CharField(max_length=255))
    name__in = ListField(child=CharField(max_length=255))
    price__gte = DecimalField(decimal_places=4, max_digits=19)
    price__lte = DecimalField(decimal_places=4, max_digits=19)
