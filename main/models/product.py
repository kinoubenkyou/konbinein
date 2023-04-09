from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    Model,
    UniqueConstraint,
)

from main.models.organization import Organization


class Product(Model):
    class Meta:
        constraints = (
            UniqueConstraint(
                "code",
                "organization",
                name="main_product_code_organization_id",
            ),
        )

    code = CharField(max_length=255, unique=True)
    name = CharField(max_length=255)
    organization = ForeignKey(Organization, on_delete=CASCADE)
    price = DecimalField(decimal_places=4, max_digits=19)
