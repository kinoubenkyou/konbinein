from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    IntegerField,
    Model,
)


class Organization(Model):
    code = CharField(max_length=255, unique=True)
    name = CharField(max_length=255)


class Order(Model):
    code = CharField(max_length=255, unique=True)
    created_at = DateTimeField()
    organization = ForeignKey(Organization, on_delete=CASCADE)


class OrderItem(Model):
    name = CharField(max_length=255)
    order = ForeignKey(Order, on_delete=CASCADE)
    quantity = IntegerField()
    unit_price = DecimalField(decimal_places=4, max_digits=19)
