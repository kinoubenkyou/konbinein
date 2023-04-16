from rest_framework.fields import CharField, DecimalField, ListField
from rest_framework.serializers import Serializer


class ProductShippingFilterSet(Serializer):
    code__in = ListField(child=CharField(max_length=255))
    fee__gte = DecimalField(decimal_places=4, max_digits=19)
    fee__lte = DecimalField(decimal_places=4, max_digits=19)
    name__in = ListField(child=CharField(max_length=255))
    shipping_type__in = ListField(child=CharField(max_length=255))
    zones__overlap = ListField(child=CharField(max_length=255))
