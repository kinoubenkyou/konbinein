from rest_framework.fields import CharField, DateTimeField, DecimalField, ListField
from rest_framework.serializers import Serializer


class OrderFilterSet(Serializer):
    code__in = ListField(child=CharField(max_length=255))
    created_at__gte = DateTimeField()
    created_at__lte = DateTimeField()
    product_total__gte = DecimalField(decimal_places=4, max_digits=19)
    product_total__lte = DecimalField(decimal_places=4, max_digits=19)
    productitem__name__in = ListField(child=CharField(max_length=255))
    total__gte = DecimalField(decimal_places=4, max_digits=19)
    total__lte = DecimalField(decimal_places=4, max_digits=19)
