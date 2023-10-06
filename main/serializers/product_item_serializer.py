from decimal import Decimal

from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.product import Product
from main.models.product_item import ProductItem
from main.serializers import _write_nested_objects
from main.serializers.product_shipping_item_serializer import (
    ProductShippingItemSerializer,
)


class ProductItemSerializer(ModelSerializer):
    class Meta:
        fields = (
            "id",
            "item_total",
            "name",
            "product",
            "price",
            "productshippingitem_set",
            "quantity",
            "shipping_total",
            "subtotal",
            "total",
        )
        model = ProductItem

    id = IntegerField(required=False)
    product = PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    productshippingitem_set = ProductShippingItemSerializer(many=True)

    @atomic
    def create(self, validated_data):
        product_item_attributes = {**validated_data}
        product_shipping_item_data_list = product_item_attributes.pop(
            "productshippingitem_set", ()
        )
        product_item = super().create(product_item_attributes)
        _write_nested_objects(
            product_shipping_item_data_list,
            {},
            "product_item",
            product_item,
            ProductShippingItemSerializer(),
        )
        return product_item

    @atomic
    def update(self, instance, validated_data):
        product_item_attributes = {**validated_data}
        product_shipping_item_data_list = product_item_attributes.pop(
            "productshippingitem_set", ()
        )
        product_shipping_item_dict = {
            product_shipping_item.id: product_shipping_item
            for product_shipping_item in instance.productshippingitem_set.all()
        }
        product_item = super().update(instance, product_item_attributes)
        _write_nested_objects(
            product_shipping_item_data_list,
            product_shipping_item_dict,
            "product_item",
            product_item,
            ProductShippingItemSerializer(),
        )
        return product_item

    def validate(self, data):
        item_total = Decimal(data["item_total"])
        if item_total != Decimal(data["price"]) * int(data["quantity"]):
            raise ValidationError(detail="Item total is incorrect.")
        subtotal = Decimal(data["subtotal"])
        if subtotal != item_total:
            raise ValidationError(detail="Subtotal is incorrect.")
        if Decimal(data["total"]) != subtotal + Decimal(data["shipping_total"]):
            raise ValidationError(detail="Total is incorrect.")
        return data

    def validate_id(self, value):
        if value is not None and self.context["instance"] is None:
            raise ValidationError(detail="Product item does not belong to order.")
        return value

    def validate_product(self, value):
        if value.organization_id != int(self.context["view"].kwargs["organization_id"]):
            raise ValidationError(detail="Product is in another organization.")
        return value

    def to_internal_value(self, data):
        instance = ProductItem.objects.filter(
            id=data.get("id"), order_id=data["order_id"]
        ).first()
        self.context["instance"] = instance
        for product_shipping_item_data in data["productshippingitem_set"]:
            product_shipping_item_data["product_item_id"] = (
                instance.id if instance is not None else None
            )
            product_shipping_item_data["quantity"] = data["quantity"]
        return super().to_internal_value(data)
