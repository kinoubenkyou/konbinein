from random import choice
from string import ascii_uppercase

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models.product import Product


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    code = Sequence(lambda n: f"code-{choice(ascii_uppercase)}{n}")
    name = Sequence(lambda n: f"name-{choice(ascii_uppercase)}{n}")
    organization = SubFactory(OrganizationFactory)
    price = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
