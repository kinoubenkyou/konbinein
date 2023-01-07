from django.db import transaction
from rest_framework.fields import DecimalField, IntegerField
from rest_framework.serializers import ModelSerializer

from main.models import Order, OrderItem, Organization


class OrderItemSerializer(ModelSerializer):
    id = IntegerField(required=False)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ["id", "name", "quantity", "total", "unit_price"]
        model = OrderItem


class OrderSerializer(ModelSerializer):
    orderitem_set = OrderItemSerializer(allow_empty=False, many=True)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ["code", "created_at", "id", "orderitem_set", "organization", "total"]
        model = Order

    @transaction.atomic
    def create(self, validated_data):
        data_list = validated_data.pop("orderitem_set", [])
        order = super().create(validated_data)
        for data in data_list:
            OrderItemSerializer().create(data | {"order": order})
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        data_list = validated_data.pop("orderitem_set", [])
        super().update(instance, validated_data)
        order_item_dict = {
            order_item.id: order_item for order_item in instance.orderitem_set.all()
        }
        for data in data_list:
            _id = data.get("id", None)
            if _id is None:
                OrderItemSerializer().create(data | {"order": instance})
            else:
                OrderItemSerializer().update(order_item_dict[_id], data)
        for _id, order_item in order_item_dict.items():
            if _id not in (data.get("id", None) for data in data_list):
                order_item.delete()
        return instance


class OrganizationSerializer(ModelSerializer):
    class Meta:
        fields = ["id", "name"]
        model = Organization
