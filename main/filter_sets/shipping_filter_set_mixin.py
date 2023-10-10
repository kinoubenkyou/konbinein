from rest_framework.fields import CharField, DecimalField, ListField
from rest_framework.serializers import SerializerMetaclass


class ShippingFilterSetMixin(metaclass=SerializerMetaclass):
    code__icontains = CharField(max_length=255)
    fixed_fee__gte = DecimalField(decimal_places=4, max_digits=19)
    fixed_fee__lte = DecimalField(decimal_places=4, max_digits=19)
    name__icontains = CharField(max_length=255)
    unit_fee__gte = DecimalField(decimal_places=4, max_digits=19)
    unit_fee__lte = DecimalField(decimal_places=4, max_digits=19)
    zones__overlap = ListField(child=CharField(max_length=255))
