from datetime import timezone

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.models import Order, OrderItem


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = Sequence(lambda n: f"code{n}")
    created_at = Faker("past_datetime", tzinfo=timezone.utc)


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    name = Sequence(lambda n: f"name{n}")
    order = SubFactory(OrderFactory)
    quantity = Faker("pyint", max_value=100, min_value=1)
    unit_price = Faker("pydecimal", left_digits=2, positive=True, right_digits=2)
