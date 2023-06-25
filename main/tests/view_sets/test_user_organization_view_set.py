from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.organization_factory import OrganizationFactory
from main.tests.user_test_case import UserTestCase


class UserOrganizationViewSetTestCase(UserTestCase):
    def test_list__paginate(self):
        organizations = OrganizationFactory.create_batch(4)
        organizations.sort(key=lambda organization: organization.id)
        organization_dicts = [
            {"object": organization} for organization in organizations[1:3]
        ]
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json()["results"], organization_dicts, True)

    def test_list__search__code(self):
        codes = ["search1", "search2"]
        organization_dicts = [
            {"object": organization}
            for organization in OrganizationFactory.create_batch(
                2, code=Iterator(codes)
            )
        ]
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        response = self.client.get(path, data={"search": "search"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), organization_dicts, False)

    def test_list__sort__code(self):
        organizations = OrganizationFactory.create_batch(2)
        organizations.sort(key=lambda organization: organization.code)
        organization_dicts = [
            {"object": organization} for organization in organizations
        ]
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), organization_dicts, True)

    def _assert_get_response(
        self, organization_data_list, organization_dicts, is_ordered
    ):
        if not is_ordered:
            organization_data_list.sort(
                key=lambda organization_data: organization_data["id"]
            )
            organization_dicts.sort(
                key=lambda organization_dict: organization_dict["object"].id
            )
        organizations = [
            organization_dict["object"] for organization_dict in organization_dicts
        ]
        expected = [
            {
                "code": organization.code,
                "id": organization.id,
                "name": organization.name,
            }
            for organization in organizations
        ]
        self.assertEqual(organization_data_list, expected)
