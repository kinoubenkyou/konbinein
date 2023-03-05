from main.factories.organization_factory import OrganizationFactory
from main.factories.personnel_factory import PersonnelFactory
from main.test_cases.user_test_case import UserTestCase


class OrganizationUserTestCase(UserTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        organization = OrganizationFactory.create()
        PersonnelFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=organization,
            user=cls.user,
        )
        cls.organization = organization
