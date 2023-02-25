from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.factories.user_factory import UserFactory
from main.models.personnel import Personnel


class PersonnelFactory(DjangoModelFactory):
    class Meta:
        model = Personnel

    does_organization_agree = Faker("boolean")
    does_user_agree = Faker("boolean")
    organization = SubFactory(OrganizationFactory)
    user = SubFactory(UserFactory)
