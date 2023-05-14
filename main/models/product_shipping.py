from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    ManyToManyField,
    Model,
    UniqueConstraint,
)

from main.models import ZONE_CHOICES
from main.models.organization import Organization
from main.models.product import Product


class ProductShipping(Model):
    class Meta:
        constraints = (
            UniqueConstraint(
                "code",
                "organization",
                name="main_product_shipping_rule_code_organization_id",
            ),
        )

    code = CharField(max_length=255)
    fixed_fee = DecimalField(decimal_places=4, max_digits=19)
    name = CharField(max_length=255)
    organization = ForeignKey(Organization, on_delete=CASCADE)
    products = ManyToManyField(Product)
    unit_fee = DecimalField(decimal_places=4, max_digits=19)
    zones = ArrayField(CharField(max_length=255, choices=ZONE_CHOICES))
