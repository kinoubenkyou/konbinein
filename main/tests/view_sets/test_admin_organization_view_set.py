from main.factories.organization_factory import OrganizationFactory
from main.tests.view_sets.admin_test_case import AdminTestCase
from main.view_sets.admin_organization_view_set import AdminOrganizationViewSet


class AdminOrganizationViewSetTestCase(AdminTestCase):
    basename = "admin-organization"
    view_set = AdminOrganizationViewSet

    def test_create(self):
        data = self._get_deserializer_data()
        filter_ = {**data}
        del filter_["user"]
        self._act_and_assert_create_test(data, filter_)

    @classmethod
    def _get_deserializer_data(cls):
        organization = OrganizationFactory.build()
        return {
            "code": organization.code,
            "name": organization.name,
            "user": cls.user.id,
        }
