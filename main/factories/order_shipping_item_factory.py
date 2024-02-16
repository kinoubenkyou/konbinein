from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from main.factories.order_factory import OrderFactory
from main.factories.order_shipping_factory import OrderShippingFactory
from main.factories.shipping_item_factory import ShippingItemFactoryMixin
from main.models.order_shipping_item import OrderShippingItem


class OrderShippingItemFactory(ShippingItemFactoryMixin, DjangoModelFactory):
    class Meta:
        model = OrderShippingItem

    item_total = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    order = SubFactory(OrderFactory)
    order_shipping = SubFactory(OrderShippingFactory)
