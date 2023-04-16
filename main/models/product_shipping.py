from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    Model,
    UniqueConstraint,
)

from main.models import ZONE_CHOICES
from main.models.organization import Organization


class ProductShipping(Model):
    class Meta:
        constraints = (
            UniqueConstraint(
                "code",
                "organization",
                name="main_product_shipping_rule_code_organization_id",
            ),
        )

    FIXED_TYPE = "fixed"
    PER_UNIT_TYPE = "per_unit"
    SHIPPING_TYPE_CHOICES = (
        (FIXED_TYPE, FIXED_TYPE),
        (PER_UNIT_TYPE, PER_UNIT_TYPE),
    )

    code = CharField(max_length=255)
    fee = DecimalField(decimal_places=4, max_digits=19)
    name = CharField(max_length=255)
    organization = ForeignKey(Organization, on_delete=CASCADE)
    shipping_type = CharField(max_length=255, choices=SHIPPING_TYPE_CHOICES)
    zones = ArrayField(CharField(max_length=255, choices=ZONE_CHOICES))
