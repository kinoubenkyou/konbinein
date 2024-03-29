from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Model,
    UniqueConstraint,
)

from main.models.organization import Organization


class Order(Model):
    class Meta:
        constraints = (
            UniqueConstraint(
                "code",
                "organization",
                name="main_order_code_organization_id",
            ),
        )

    code = CharField(max_length=255)
    created_at = DateTimeField()
    order_shipping_total = DecimalField(decimal_places=4, max_digits=19)
    organization = ForeignKey(Organization, on_delete=CASCADE)
    product_shipping_total = DecimalField(decimal_places=4, max_digits=19)
    product_total = DecimalField(decimal_places=4, max_digits=19)
    total = DecimalField(decimal_places=4, max_digits=19)
