from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models.order import Order


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = Sequence(lambda n: f"code{n}")
    created_at = Faker("past_datetime")
    organization = SubFactory(OrganizationFactory)
    product_total = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    total = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
