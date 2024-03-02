from factory import Iterator

from main.factories.organization_factory import OrganizationFactory
from main.tests.user_test_case import UserTestCase
from main.tests.view_sets.user_view_set_test_case_mixin import UserViewSetTestCaseMixin
from main.view_sets.user_organization_view_set import UserOrganizationViewSet


class UserOrganizationViewSetTestCase(UserViewSetTestCaseMixin, UserTestCase):
    basename = "user-organization"
    view_set = UserOrganizationViewSet

    def test_list__filter__code__icontains(self):
        OrganizationFactory.create()
        OrganizationFactory.create_batch(
            2, code=Iterator(range(2), getter=lambda n: f"-code--{n}")
        )
        self._act_and_assert_list_test({"code__icontains": "code--"})

    def test_list__filter__name__icontains(self):
        OrganizationFactory.create()
        OrganizationFactory.create_batch(
            2, name=Iterator(range(2), getter=lambda n: f"-name--{n}")
        )
        self._act_and_assert_list_test({"name__icontains": "name--"})

    def test_list__paginate(self):
        OrganizationFactory.create_batch(4)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__code(self):
        OrganizationFactory.create_batch(2)
        self._act_and_assert_list_test({"ordering": "code"})

    @staticmethod
    def _serializer_data(organization):
        return {
            "code": organization.code,
            "id": organization.id,
            "name": organization.name,
        }
