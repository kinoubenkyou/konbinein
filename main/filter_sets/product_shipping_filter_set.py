from rest_framework.fields import CharField, DecimalField, ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer

from main.models.product import Product


class ProductShippingFilterSet(Serializer):
    code__icontains = CharField(max_length=255)
    fixed_fee__gte = DecimalField(decimal_places=4, max_digits=19)
    fixed_fee__lte = DecimalField(decimal_places=4, max_digits=19)
    name__icontains = CharField(max_length=255)
    products__in = ListField(
        child=PrimaryKeyRelatedField(queryset=Product.objects.all())
    )
    unit_fee__gte = DecimalField(decimal_places=4, max_digits=19)
    unit_fee__lte = DecimalField(decimal_places=4, max_digits=19)
    zones__overlap = ListField(child=CharField(max_length=255))
