from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.models import ZONE_CHOICES
from main.models.product_shipping import ProductShipping


class ProductShippingFactory(DjangoModelFactory):
    class Meta:
        model = ProductShipping

    code = Sequence(lambda n: f"code{n}")
    fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=2)
    name = Sequence(lambda n: f"name{n}")
    organization = SubFactory(OrganizationFactory)
    shipping_type = Faker(
        "random_element",
        elements=tuple(choice[0] for choice in ProductShipping.SHIPPING_TYPE_CHOICES),
    )
    zones = Faker(
        "random_choices", elements=tuple(choice[0] for choice in ZONE_CHOICES), length=2
    )
