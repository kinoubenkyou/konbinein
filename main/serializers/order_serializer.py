from decimal import Decimal

from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.order import Order
from main.serializers import _write_nested_objects
from main.serializers.order_shipping_item_serializer import OrderShippingItemSerializer
from main.serializers.product_item_serializer import ProductItemSerializer


class OrderSerializer(ModelSerializer):
    class Meta:
        fields = (
            "code",
            "created_at",
            "id",
            "order_shipping_total",
            "ordershippingitem_set",
            "product_shipping_total",
            "product_total",
            "productitem_set",
            "total",
        )
        model = Order

    ordershippingitem_set = OrderShippingItemSerializer(many=True)
    productitem_set = ProductItemSerializer(allow_empty=False, many=True)

    @atomic
    def create(self, validated_data):
        order_attributes = {
            **validated_data,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        order_shipping_item_data_list = order_attributes.pop(
            "ordershippingitem_set", ()
        )
        product_item_data_list = order_attributes.pop("productitem_set", ())
        order = super().create(order_attributes)
        _write_nested_objects(
            order_shipping_item_data_list,
            {},
            "order",
            order,
            False,
            OrderShippingItemSerializer,
        )
        _write_nested_objects(
            product_item_data_list, {}, "order", order, False, ProductItemSerializer
        )
        return order

    def to_internal_value(self, data):
        order_shipping_items = (
            [] if self.instance is None else self.instance.ordershippingitem_set.all()
        )
        order_shipping_item_dict = {
            order_shipping_item.id: order_shipping_item
            for order_shipping_item in order_shipping_items
        }
        for order_shipping_item_data in data["ordershippingitem_set"]:
            order_shipping_item_data["instance"] = order_shipping_item_dict.get(
                order_shipping_item_data.get("id")
            )
            order_shipping_item_data["quantity"] = len(data["productitem_set"])
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
        order_shipping_item_data_list = order_attributes.pop(
            "ordershippingitem_set", ()
        )
        order_shipping_item_dict = {
            order_shipping_item.id: order_shipping_item
            for order_shipping_item in instance.ordershippingitem_set.all()
        }
        product_item_data_list = order_attributes.pop("productitem_set", ())
        product_item_dict = {
            product_item.id: product_item
            for product_item in instance.productitem_set.all()
        }
        order = super().update(instance, order_attributes)
        _write_nested_objects(
            order_shipping_item_data_list,
            order_shipping_item_dict,
            "order",
            order,
            self.partial,
            OrderShippingItemSerializer,
        )
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
        order_shipping_total = Decimal(data["order_shipping_total"])
        if order_shipping_total != sum(
            Decimal(order_shipping_item_data["item_total"])
            for order_shipping_item_data in data["ordershippingitem_set"]
        ):
            raise ValidationError(detail="Order shipping total is incorrect.")
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
        if (
            Decimal(data["total"])
            != order_shipping_total + product_total + product_shipping_total
        ):
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
