from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DecimalField,
    ForeignKey,
    Model,
)

from main.models.product_item import ProductItem
from main.models.product_shipping import ProductShipping


class ProductShippingItem(Model):
    fixed_fee = DecimalField(decimal_places=4, max_digits=19)
    item_total = DecimalField(decimal_places=4, max_digits=19)
    name = CharField(max_length=255)
    product_item = ForeignKey(ProductItem, on_delete=CASCADE)
    product_shipping = ForeignKey(ProductShipping, null=True, on_delete=SET_NULL)
    unit_fee = DecimalField(decimal_places=4, max_digits=19)
