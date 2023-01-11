from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    EmailField,
    ForeignKey,
    IntegerField,
    Model,
)


class Organization(Model):
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


class User(Model):
    email = EmailField(unique=True)
    hashed_password = CharField(max_length=255)
    name = CharField(max_length=255, null=True)
    USERNAME_FIELD = "email"
