from datetime import timezone

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models.order import Order


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = Sequence(lambda n: f"code{n}")
    created_at = Faker("past_datetime", tzinfo=timezone.utc)
    organization = SubFactory(OrganizationFactory)