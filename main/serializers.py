from rest_framework.fields import DecimalField
from rest_framework.serializers import ModelSerializer

from main.models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ["name", "quantity", "total", "unit_price"]
        model = OrderItem


class OrderSerializer(ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ["code", "created_at", "id", "orderitem_set", "total"]
        model = Order

    def create(self, validated_data):
        orderitem_set = validated_data.pop("orderitem_set")
        order = super().create(validated_data)
        objects = [OrderItem(order=order, **order_item) for order_item in orderitem_set]
        OrderItem.objects.bulk_create(objects)
        order.refresh_from_db()
        return order
