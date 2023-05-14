from rest_framework.fields import CharField, DecimalField, IntegerField, ListField
from rest_framework.serializers import Serializer


class ProductShippingFilterSet(Serializer):
    code__in = ListField(child=CharField(max_length=255))
    fixed_fee__gte = DecimalField(decimal_places=4, max_digits=19)
    fixed_fee__lte = DecimalField(decimal_places=4, max_digits=19)
    name__in = ListField(child=CharField(max_length=255))
    products__id__in = ListField(child=IntegerField())
    unit_fee__gte = DecimalField(decimal_places=4, max_digits=19)
    unit_fee__lte = DecimalField(decimal_places=4, max_digits=19)
    zones__overlap = ListField(child=CharField(max_length=255))
