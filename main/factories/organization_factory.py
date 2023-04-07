from factory import Sequence
from factory.django import DjangoModelFactory

from main.models.organization import Organization


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    code = Sequence(lambda n: f"name{n}")
    name = Sequence(lambda n: f"name{n}")
