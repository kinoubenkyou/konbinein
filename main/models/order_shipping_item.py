from django.db.models import CASCADE, SET_NULL, ForeignKey

from main.models.order import Order
from main.models.order_shipping import OrderShipping
from main.models.shipping_item import ShippingItem


class OrderShippingItem(ShippingItem):
    order = ForeignKey(Order, on_delete=CASCADE)
    order_shipping = ForeignKey(OrderShipping, null=True, on_delete=SET_NULL)
