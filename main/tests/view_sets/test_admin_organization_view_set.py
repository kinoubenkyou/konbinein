from main.factories.organization_factory import OrganizationFactory
from main.tests.admin_test_case import AdminTestCase
from main.tests.view_sets.authenticated_view_set_test_case_mixin import (
    AuthenticatedViewSetTestCaseMixin,
)
from main.tests.view_sets.view_set_test_case_mixin import ViewSetTestCaseMixin
from main.view_sets.admin_organization_view_set import AdminOrganizationViewSet


class AdminOrganizationViewSetTestCase(
    AuthenticatedViewSetTestCaseMixin, ViewSetTestCaseMixin, AdminTestCase
):
    basename = "admin-organization"
    view_set = AdminOrganizationViewSet

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
