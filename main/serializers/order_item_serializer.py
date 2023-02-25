from rest_framework.fields import DecimalField, IntegerField
from rest_framework.serializers import ModelSerializer

from main.models.order_item import OrderItem


class OrderItemSerializer(ModelSerializer):
    id = IntegerField(required=False)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ("id", "name", "quantity", "total", "unit_price")
        model = OrderItem
