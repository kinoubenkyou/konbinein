from factory.django import DjangoModelFactory

from main.factories.shipping_factory import ShippingFactoryMixin
from main.models.order_shipping import OrderShipping


class OrderShippingFactory(ShippingFactoryMixin, DjangoModelFactory):
    class Meta:
        model = OrderShipping
