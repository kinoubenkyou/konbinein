from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
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

    code = CharField(max_length=255, unique=True)
    created_at = DateTimeField()
    organization = ForeignKey(Organization, on_delete=CASCADE)

    @property
    def total(self):
        order_items = self.orderitem_set.all()
        return sum(order_item.total for order_item in order_items)
