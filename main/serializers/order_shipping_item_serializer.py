from decimal import Decimal

from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.order_shipping import OrderShipping
from main.models.order_shipping_item import OrderShippingItem


class OrderShippingItemSerializer(ModelSerializer):
    class Meta:
        fields = (
            "fixed_fee",
            "id",
            "item_total",
            "name",
            "order_shipping",
            "unit_fee",
        )
        model = OrderShippingItem

    id = IntegerField(required=False)
    order_shipping = PrimaryKeyRelatedField(
        queryset=OrderShipping.objects.all(), required=True
    )

    def to_internal_value(self, data):
        self.instance = data.pop("instance")
        self.context["quantity"] = data.pop("quantity")
        return super().to_internal_value(data)

    def validate(self, data):
        if Decimal(data["item_total"]) != Decimal(data["fixed_fee"]) + Decimal(
            data["unit_fee"]
        ) * int(self.context["quantity"]):
            raise ValidationError(detail="Item total is incorrect.")
        return data

    def validate_id(self, value):
        if self.instance is None:
            raise ValidationError(
                detail="Order shipping item doesn't belong to the order."
            )
        return value

    def validate_order_shipping(self, value):
        if value.organization_id != int(self.context["view"].kwargs["organization_id"]):
            raise ValidationError(
                detail="Order shipping doesn't belong to the organization."
            )
        return value
