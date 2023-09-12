from decimal import Decimal

from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.order import Order
from main.serializers.product_item_serializer import ProductItemSerializer
from main.serializers.write_nested_mixin import WriteNestedMixin


class OrderSerializer(WriteNestedMixin, ModelSerializer):
    class Meta:
        fields = (
            "code",
            "created_at",
            "id",
            "productitem_set",
            "product_total",
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
        self._write_nested_objects(
            product_item_data_list, {}, "order", order, ProductItemSerializer()
        )
        return order

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
        self._write_nested_objects(
            product_item_data_list,
            product_item_dict,
            "order",
            order,
            ProductItemSerializer(),
        )
        return order

    def validate(self, data):
        product_total = Decimal(data["product_total"])
        if product_total != sum(
            Decimal(product_item_data["total"])
            for product_item_data in data["productitem_set"]
        ):
            raise ValidationError(detail="Product total is incorrect.")
        if Decimal(data["total"]) != product_total:
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

    def to_internal_value(self, data):
        for product_item_data in data["productitem_set"]:
            product_item_data["order_id"] = (
                self.instance.id if self.instance is not None else None
            )
        return super().to_internal_value(data)
