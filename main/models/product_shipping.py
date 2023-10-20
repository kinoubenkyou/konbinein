from django.db.models import ManyToManyField, UniqueConstraint

from main.models.product import Product
from main.models.shipping import Shipping


class ProductShipping(Shipping):
    class Meta:
        constraints = (
            UniqueConstraint(
                "code",
                "organization",
                name="main_product_shipping_code_organization_id",
            ),
        )

    products = ManyToManyField(Product, blank=True)
