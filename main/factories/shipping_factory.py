from random import choice
from string import ascii_uppercase

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models import ZONE_CHOICES


class ShippingFactoryMixin(DjangoModelFactory):
    code = Sequence(lambda n: f"code-{choice(ascii_uppercase)}{n}")
    fixed_fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    name = Sequence(lambda n: f"name-{choice(ascii_uppercase)}{n}")
    organization = SubFactory(OrganizationFactory)
    unit_fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    zones = Faker(
        "random_choices", elements=[choice[0] for choice in ZONE_CHOICES], length=2
    )
