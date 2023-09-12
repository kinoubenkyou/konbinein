from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    Model,
)

from main.models.order import Order
from main.models.product import Product


class ProductItem(Model):
    item_total = DecimalField(decimal_places=4, max_digits=19)
    name = CharField(max_length=255)
    order = ForeignKey(Order, on_delete=CASCADE)
    price = DecimalField(decimal_places=4, max_digits=19)
    product = ForeignKey(Product, null=True, on_delete=SET_NULL)
    quantity = IntegerField()
    shipping_total = DecimalField(decimal_places=4, max_digits=19)
    subtotal = DecimalField(decimal_places=4, max_digits=19)
    total = DecimalField(decimal_places=4, max_digits=19)
