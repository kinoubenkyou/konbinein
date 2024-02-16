from django.db.models import CASCADE, SET_NULL, ForeignKey

from main.models.product_item import ProductItem
from main.models.product_shipping import ProductShipping
from main.models.shipping_item import ShippingItem


class ProductShippingItem(ShippingItem):
    product_item = ForeignKey(ProductItem, on_delete=CASCADE)
    product_shipping = ForeignKey(ProductShipping, null=True, on_delete=SET_NULL)
