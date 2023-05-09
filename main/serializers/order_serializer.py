from decimal import Decimal

from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.order import Order
from main.serializers.product_item_serializer import ProductItemSerializer


class OrderSerializer(ModelSerializer):
    class Meta:
        fields = ("code", "created_at", "id", "productitem_set", "total")
        model = Order

    productitem_set = ProductItemSerializer(allow_empty=False, many=True)

    @atomic
    def create(self, validated_data):
        order_attributes = validated_data | {
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        product_item_data_list = order_attributes.pop("productitem_set", ())
        order = super().create(order_attributes)
        for product_item_data in product_item_data_list:
            ProductItemSerializer().create(product_item_data | {"order": order})
        return order

    @atomic
    def update(self, instance, validated_data):
        order_attributes = validated_data | {
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        product_item_data_list = order_attributes.pop("productitem_set", ())
        product_item_dict = {
            product_item.id: product_item
            for product_item in instance.productitem_set.all()
        }
        order = super().update(instance, order_attributes)
        for product_item_data in product_item_data_list:
            product_item_id = product_item_data.get("id")
            if product_item_id is None:
                ProductItemSerializer().create(product_item_data | {"order": order})
            else:
                ProductItemSerializer().update(
                    product_item_dict[product_item_id], product_item_data
                )
        for product_item_id, product_item in product_item_dict.items():
            if product_item_id not in (
                data.get("id") for data in product_item_data_list
            ):
                product_item.delete()
        return order

    def validate(self, data):
        calculated_total = sum(
            Decimal(product_item_data["price"]) * int(product_item_data["quantity"])
            for product_item_data in data["productitem_set"]
        )
        if Decimal(data["total"]) != calculated_total:
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
