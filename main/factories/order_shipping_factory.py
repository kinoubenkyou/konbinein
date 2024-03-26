from main.factories.shipping_factory import ShippingFactory
from main.models.order_shipping import OrderShipping


class OrderShippingFactory(ShippingFactory):
    class Meta:
        model = OrderShipping
