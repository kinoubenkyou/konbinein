from factory import SubFactory
from factory.django import DjangoModelFactory

from main.factories.organization_factory import OrganizationFactory
from main.factories.user_factory import UserFactory
from main.models.staff import Staff
from main.tests import faker


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = Staff

    does_organization_agree = faker.boolean()
    does_user_agree = faker.boolean()
    organization = SubFactory(OrganizationFactory)
    user = SubFactory(UserFactory)
