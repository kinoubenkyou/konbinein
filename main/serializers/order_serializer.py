from django.db import transaction
from rest_framework.fields import DecimalField
from rest_framework.serializers import ModelSerializer

from main.models.order import Order
from main.serializers.order_item_serializer import OrderItemSerializer


class OrderSerializer(ModelSerializer):
    orderitem_set = OrderItemSerializer(allow_empty=False, many=True)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ("code", "created_at", "id", "orderitem_set", "organization", "total")
        model = Order

    def to_internal_value(self, data):
        data["organization"] = self.context["view"].kwargs["organization_id"]
        return super().to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data):
        data_list = validated_data.pop("orderitem_set", ())
        order = super().create(validated_data)
        for data in data_list:
            OrderItemSerializer().create(data | {"order": order})
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        data_list = validated_data.pop("orderitem_set", ())
        super().update(instance, validated_data)
        order_item_dict = {
            order_item.id: order_item for order_item in instance.orderitem_set.all()
        }
        for data in data_list:
            id_ = data.get("id")
            if id_ is None:
                OrderItemSerializer().create(data | {"order": instance})
            else:
                OrderItemSerializer().update(order_item_dict[id_], data)
        for id_, order_item in order_item_dict.items():
            if id_ not in (data.get("id") for data in data_list):
                order_item.delete()
        return instance
