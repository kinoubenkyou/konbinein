from random import choice
from string import ascii_uppercase

from factory import Sequence
from factory.django import DjangoModelFactory

from main.models.organization import Organization


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    code = Sequence(lambda n: f"code-{choice(ascii_uppercase)}{n}")
    name = Sequence(lambda n: f"name-{choice(ascii_uppercase)}{n}")
