from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models.order import Order
from main.tests import faker


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = Sequence(lambda n: f"code{n}")
    created_at = faker.past_datetime()
    organization = SubFactory(OrganizationFactory)
