from main.factories.organization_factory import OrganizationFactory
from main.factories.staff_factory import StaffFactory
from main.tests.user_test_case import UserTestCase


class StaffTestCase(UserTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.organization = OrganizationFactory.create()
        cls.staff = StaffFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=cls.organization,
            user=cls.user,
        )
