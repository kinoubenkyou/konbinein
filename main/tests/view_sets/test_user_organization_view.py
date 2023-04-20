from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.organization_factory import OrganizationFactory
from main.test_cases.user_test_case import UserTestCase


class UserOrganizationViewSetTestCase(UserTestCase):
    def test_list__paginate(self):
        organizations = OrganizationFactory.create_batch(4)
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        organizations.sort(key=lambda organization: organization.id)
        self._assertGetResponseData(
            response.json()["results"],
            (organizations[1], organizations[2]),
            is_ordered=True,
        )

    def test_list__search__code(self):
        codes = ("search1", "search2")
        organizations = OrganizationFactory.create_batch(2, code=Iterator(codes))
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        response = self.client.get(path, data={"search": "search"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), organizations)

    def test_list__sort__code(self):
        organizations = OrganizationFactory.create_batch(2)
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        organizations.sort(key=lambda organization: organization.code)
        self._assertGetResponseData(response.json(), organizations, is_ordered=True)

    def _assertGetResponseData(self, actual, organizations, is_ordered=False):
        expected = [
            {
                "code": organization.code,
                "id": organization.id,
                "name": organization.name,
            }
            for organization in organizations
        ]
        if is_ordered:
            self.assertEqual(actual, expected)
        else:
            self.assertCountEqual(actual, expected)
