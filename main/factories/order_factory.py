from random import choice
from string import ascii_uppercase

from factory import Faker, LazyAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models.order import Order


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = Sequence(lambda n: f"code-{choice(ascii_uppercase)}{n}")
    created_at = Faker("past_datetime")
    organization = SubFactory(OrganizationFactory)
    product_shipping_total = Faker(
        "pydecimal", left_digits=2, positive=True, right_digits=4
    )
    product_total = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    total = LazyAttribute(lambda order: order.product_total)
