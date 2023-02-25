from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    Model,
)

from main.models.order import Order


class OrderItem(Model):
    name = CharField(max_length=255)
    order = ForeignKey(Order, on_delete=CASCADE)
    quantity = IntegerField()
    unit_price = DecimalField(decimal_places=4, max_digits=19)
