from rest_framework.fields import CharField, DecimalField
from rest_framework.serializers import Serializer


class ProductFilterSet(Serializer):
    code__icontains = CharField(max_length=255)
    name__icontains = CharField(max_length=255)
    price__gte = DecimalField(decimal_places=4, max_digits=19)
    price__lte = DecimalField(decimal_places=4, max_digits=19)
