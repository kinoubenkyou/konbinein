from django.db.models import UniqueConstraint

from main.models.shipping import Shipping


class OrderShipping(Shipping):
    class Meta:
        constraints = (
            UniqueConstraint(
                "code",
                "organization",
                name="main_order_shipping_code_organization_id",
            ),
        )
