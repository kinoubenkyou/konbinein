from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.tests.view_sets.organization_test_case import OrganizationTestCase
from main.view_sets.organization_organization_view_set import (
    OrganizationOrganizationViewSet,
)


class OrganizationOrganizationViewSetTestCase(OrganizationTestCase):
    basename = "organization-organization"
    view_set = OrganizationOrganizationViewSet

    def test_destroy(self):
        self._act_and_assert_destroy_test(self.organization)

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(self.organization.id)

    def test_update(self):
        data = self._get_deserializer_data()
        filter_ = {**data}
        self._act_and_assert_update_test(data, filter_, self.organization.id)

    @staticmethod
    def _get_deserializer_data():
        organization = OrganizationFactory.build()
        return {"code": organization.code, "name": organization.name}

    def _get_query_set(self):
        return Organization.objects.filter(id=self.organization.id)

    @staticmethod
    def _get_serializer_data(organization):
        return {
            "code": organization.code,
            "id": organization.id,
            "name": organization.name,
        }
