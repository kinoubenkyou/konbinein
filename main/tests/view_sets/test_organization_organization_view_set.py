from main.factories.organization_factory import OrganizationFactory
from main.tests.view_sets.staff_test_case import StaffTestCase
from main.view_sets.organization_organization_view_set import (
    OrganizationOrganizationViewSet,
)


class OrganizationOrganizationViewSetTestCase(StaffTestCase):
    basename = "organization-organization"
    view_set = OrganizationOrganizationViewSet

    def test_destroy(self):
        self._act_and_assert_destroy_test(self.organization)

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(self.organization.id)

    def test_update(self):
        data = self._deserializer_data()
        filter_ = {**data}
        self._act_and_assert_update_test(data, filter_, self.organization.id)

    @staticmethod
    def _deserializer_data():
        organization = OrganizationFactory.build()
        return {"code": organization.code, "name": organization.name}

    @staticmethod
    def _serializer_data(organization):
        return {
            "code": organization.code,
            "id": organization.id,
            "name": organization.name,
        }
