from rest_framework.fields import CharField, DateTimeField, DecimalField, ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer

from main.models.product import Product
from main.models.product_shipping import ProductShipping


class OrderFilterSet(Serializer):
    code__icontains = CharField(max_length=255)
    created_at__gte = DateTimeField()
    created_at__lte = DateTimeField()
    product_total__gte = DecimalField(decimal_places=4, max_digits=19)
    product_total__lte = DecimalField(decimal_places=4, max_digits=19)
    productitem__product__in = ListField(
        child=PrimaryKeyRelatedField(queryset=Product.objects.all())
    )
    product_shipping_total__gte = DecimalField(decimal_places=4, max_digits=19)
    product_shipping_total__lte = DecimalField(decimal_places=4, max_digits=19)
    productitem__productshippingitem__product_shipping__in = ListField(
        child=PrimaryKeyRelatedField(queryset=ProductShipping.objects.all())
    )
    total__gte = DecimalField(decimal_places=4, max_digits=19)
    total__lte = DecimalField(decimal_places=4, max_digits=19)
