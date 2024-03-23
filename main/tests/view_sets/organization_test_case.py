from main.factories.organization_factory import OrganizationFactory
from main.factories.staff_factory import StaffFactory
from main.tests.view_sets.authenticated_test_case import AuthenticatedTestCase


class OrganizationTestCase(AuthenticatedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.organization = OrganizationFactory.create()
        StaffFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=cls.organization,
            user=cls.user,
        )

    def _path(self, action, kwargs):
        kwargs["organization_id"] = self.organization.id
        return super()._path(action, kwargs)
