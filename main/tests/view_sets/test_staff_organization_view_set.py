from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.tests.staff_test_case import StaffTestCase
from main.tests.view_sets.view_set_mixin import ViewSetTestCaseMixin


class OrganizationViewSetTestCase(ViewSetTestCaseMixin, StaffTestCase):
    basename = "organization"
    model = Organization

    def test_destroy(self):
        self._act_and_assert_destroy_test_response_status(self.organization.id)

    def test_partial_update(self):
        data = self._deserializer_data()
        filter_ = {**data}
        self._act_and_assert_partial_update_test(data, filter_, self.organization.id)

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(self.organization.id)

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
