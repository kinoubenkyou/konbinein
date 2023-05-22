from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.user_factory import UserFactory
from main.tests.staff_test_case import StaffTestCase


class OrganizationUserViewSetTestCase(StaffTestCase):
    def test_list__paginate(self):
        users = UserFactory.create_batch(3)
        users.append(self.user)
        path = reverse(
            "organization-user-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        users.sort(key=lambda user: user.id)
        self._assertGetResponseData(
            response.json()["results"], (users[1], users[2]), is_ordered=True
        )

    def test_list__search__email(self):
        emails = ("search1@email.com", "search2@email.com")
        users = UserFactory.create_batch(2, email=Iterator(emails))
        path = reverse(
            "organization-user-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"search": "search"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), users)

    def test_list__sort__email(self):
        users = [UserFactory.create(), self.user]
        path = reverse(
            "organization-user-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "email"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        users.sort(key=lambda user: user.email)
        self._assertGetResponseData(response.json(), users, is_ordered=True)

    def _assertGetResponseData(self, actual, users, is_ordered=False):
        expected = [
            {"email": user.email, "id": user.id, "name": user.name} for user in users
        ]
        if is_ordered:
            self.assertEqual(actual, expected)
        else:
            self.assertCountEqual(actual, expected)
