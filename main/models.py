from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    EmailField,
    ForeignKey,
    IntegerField,
    Model,
    UniqueConstraint,
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
    authentication_token = CharField(max_length=255, null=True, unique=True)
    email = EmailField(unique=True)
    email_verification_token = CharField(max_length=255, null=True)
    hashed_password = CharField(max_length=255)
    name = CharField(max_length=255, null=True)


class Personnel(Model):
    class Meta:
        constraints = (
            UniqueConstraint(
                "organization",
                "user",
                name="main_organizationuser_organization_id_user_id",
            ),
        )

    does_organization_agree = BooleanField()
    does_user_agree = BooleanField()
    organization = ForeignKey(Organization, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
