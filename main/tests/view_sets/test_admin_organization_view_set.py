from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.tests.admin_test_case import AdminTestCase
from main.tests.view_sets.view_set_test_case_mixin import ViewSetTestCaseMixin


class AdminOrganizationViewSetTestCase(ViewSetTestCaseMixin, AdminTestCase):
    basename = "admin-organization"
    query_set = Organization.objects.all()

    def test_create(self):
        data = self._deserializer_data()
        filter_ = {**data}
        del filter_["user"]
        self._act_and_assert_create_test(data, filter_)

    @classmethod
    def _deserializer_data(cls):
        organization = OrganizationFactory.build()
        return {
            "code": organization.code,
            "name": organization.name,
            "user": cls.user.id,
        }
