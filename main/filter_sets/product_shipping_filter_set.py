from rest_framework.fields import ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer

from main.filter_sets.shipping_filter_set_mixin import ShippingFilterSetMixin
from main.models.product import Product


class ProductShippingFilterSet(ShippingFilterSetMixin, Serializer):
    products__in = ListField(
        child=PrimaryKeyRelatedField(queryset=Product.objects.all())
    )
