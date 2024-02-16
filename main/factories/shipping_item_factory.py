from random import choice
from string import ascii_uppercase

from factory import Faker, Sequence
from factory.django import DjangoModelFactory


class ShippingItemFactoryMixin(DjangoModelFactory):
    fixed_fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    name = Sequence(lambda n: f"name-{choice(ascii_uppercase)}{n}")
    unit_fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
