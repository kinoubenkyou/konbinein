from rest_framework.serializers import Serializer

from main.filter_sets.shipping_filter_set_mixin import ShippingFilterSetMixin


class OrderShippingFilterSet(ShippingFilterSetMixin, Serializer):
    pass
