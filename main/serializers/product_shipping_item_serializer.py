from decimal import Decimal

from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.product_shipping import ProductShipping
from main.models.product_shipping_item import ProductShippingItem


class ProductShippingItemSerializer(ModelSerializer):
    class Meta:
        fields = (
            "fixed_fee",
            "id",
            "item_total",
            "name",
            "product_shipping",
            "unit_fee",
        )
        model = ProductShippingItem

    id = IntegerField(required=False)
    product_shipping = PrimaryKeyRelatedField(
        queryset=ProductShipping.objects.all(), required=True
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
                detail="Product shipping item doesn't belong to the order."
            )
        return value

    def validate_product_shipping(self, value):
        if value.organization_id != int(self.context["view"].kwargs["organization_id"]):
            raise ValidationError(
                detail="Product shipping doesn't belong to the organization."
            )
        return value
