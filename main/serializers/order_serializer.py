from django.db import transaction
from rest_framework.fields import DecimalField
from rest_framework.serializers import ModelSerializer

from main.models.order import Order
from main.serializers.order_item_serializer import OrderItemSerializer


class OrderSerializer(ModelSerializer):
    orderitem_set = OrderItemSerializer(allow_empty=False, many=True)
    total = DecimalField(decimal_places=4, max_digits=19, read_only=True)

    class Meta:
        fields = ("code", "created_at", "id", "orderitem_set", "total")
        model = Order

    @transaction.atomic
    def create(self, validated_data):
        order_attributes = validated_data | {
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        order_item_data_list = order_attributes.pop("orderitem_set", ())
        order = super().create(order_attributes)
        for order_item_data in order_item_data_list:
            OrderItemSerializer().create(order_item_data | {"order": order})
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        order_attributes = validated_data | {
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        order_item_data_list = order_attributes.pop("orderitem_set", ())
        order = super().update(instance, order_attributes)
        order_item_dict = {
            order_item.id: order_item for order_item in order.orderitem_set.all()
        }
        for order_item_data in order_item_data_list:
            order_item_id = order_item_data.get("id")
            if order_item_id is None:
                OrderItemSerializer().create(order_item_data | {"order": order})
            else:
                OrderItemSerializer().update(
                    order_item_dict[order_item_id], order_item_data
                )
        for order_item_id, order_item in order_item_dict.items():
            if order_item_id not in (data.get("id") for data in order_item_data_list):
                order_item.delete()
        return order
