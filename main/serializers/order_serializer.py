from decimal import Decimal

from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.order import Order
from main.serializers import _write_nested_objects
from main.serializers.product_item_serializer import ProductItemSerializer


class OrderSerializer(ModelSerializer):
    class Meta:
        fields = (
            "code",
            "created_at",
            "id",
            "product_shipping_total",
            "product_total",
            "productitem_set",
            "total",
        )
        model = Order

    productitem_set = ProductItemSerializer(allow_empty=False, many=True)

    @atomic
    def create(self, validated_data):
        order_attributes = {
            **validated_data,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        product_item_data_list = order_attributes.pop("productitem_set", ())
        order = super().create(order_attributes)
        _write_nested_objects(
            product_item_data_list, {}, "order", order, False, ProductItemSerializer
        )
        return order

    def to_internal_value(self, data):
        product_items = (
            [] if self.instance is None else self.instance.productitem_set.all()
        )
        product_item_dict = {
            product_item.id: product_item for product_item in product_items
        }
        for product_item_data in data["productitem_set"]:
            product_item_data["instance"] = product_item_dict.get(
                product_item_data.get("id")
            )
        return super().to_internal_value(data)

    @atomic
    def update(self, instance, validated_data):
        order_attributes = {
            **validated_data,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        product_item_data_list = order_attributes.pop("productitem_set", ())
        product_item_dict = {
            product_item.id: product_item
            for product_item in instance.productitem_set.all()
        }
        order = super().update(instance, order_attributes)
        _write_nested_objects(
            product_item_data_list,
            product_item_dict,
            "order",
            order,
            self.partial,
            ProductItemSerializer,
        )
        return order

    def validate(self, data):
        product_total = Decimal(data["product_total"])
        if product_total != sum(
            Decimal(product_item_data["item_total"])
            for product_item_data in data["productitem_set"]
        ):
            raise ValidationError(detail="Product total is incorrect.")
        product_shipping_total = Decimal(data["product_shipping_total"])
        if product_shipping_total != sum(
            Decimal(product_shipping_item_data["item_total"])
            for product_item_data in data["productitem_set"]
            for product_shipping_item_data in product_item_data[
                "productshippingitem_set"
            ]
        ):
            raise ValidationError(detail="Product shipping total is incorrect.")
        if Decimal(data["total"]) != product_total + product_shipping_total:
            raise ValidationError(detail="Total is incorrect.")
        return data

    def validate_code(self, value):
        query_set = Order.objects.filter(
            code=value, organization=self.context["view"].kwargs["organization_id"]
        )
        if self.instance is not None:
            query_set = query_set.exclude(id=self.instance.id)
        if query_set.exists():
            raise ValidationError(detail="Code is already in another order.")
        return value
