from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.user_factory import UserFactory
from main.tests.admin_test_case import AdminTestCase


class AdminUserViewSetTestCase(AdminTestCase):
    def test_list__paginate(self):
        users = UserFactory.create_batch(3)
        users.append(self.user)
        users.sort(key=lambda user: user.id)
        user_dicts = [{"object": user} for user in users[1:3]]
        path = reverse("admin-user-list")
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json()["results"], user_dicts, True)

    def test_list__search__email(self):
        emails = ["search1@email.com", "search2@email.com"]
        users = UserFactory.create_batch(2, email=Iterator(emails))
        user_dicts = [{"object": user} for user in users]
        path = reverse("admin-user-list")
        response = self.client.get(path, data={"search": "search"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), user_dicts, False)

    def test_list__sort__email(self):
        users = [UserFactory.create(), self.user]
        users.sort(key=lambda user: user.email)
        user_dicts = [{"object": user} for user in users]
        path = reverse("admin-user-list")
        response = self.client.get(path, data={"ordering": "email"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), user_dicts, True)

    def _assert_get_response(self, user_data_list, user_dicts, is_ordered):
        if not is_ordered:
            user_data_list.sort(key=lambda user_data: user_data["id"])
            user_dicts.sort(key=lambda user_dict: user_dict["object"].id)
        users = [user_dict["object"] for user_dict in user_dicts]
        expected = [
            {"email": user.email, "id": user.id, "name": user.name} for user in users
        ]
        self.assertEqual(user_data_list, expected)
