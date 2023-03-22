from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.order_factory import OrderFactory
from main.models.order_item import OrderItem
from main.tests import faker


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    name = Sequence(lambda n: f"name{n}")
    order = SubFactory(OrderFactory)
    quantity = faker.pyint(max_value=100, min_value=1)
    unit_price = faker.pydecimal(left_digits=2, positive=True, right_digits=2)
