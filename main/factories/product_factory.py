from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models.product import Product


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    code = Sequence(lambda n: f"code{n}")
    name = Sequence(lambda n: f"name{n}")
    organization = SubFactory(OrganizationFactory)
    price = Faker("pydecimal", left_digits=2, positive=True, right_digits=2)
