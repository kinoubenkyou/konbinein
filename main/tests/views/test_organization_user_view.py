from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.user_factory import UserFactory
from main.test_cases.staff_test_case import StaffTestCase


class OrganizationUserViewSetTestCase(StaffTestCase):
    def test_list(self):
        users = (self.user, UserFactory.create())
        path = reverse(
            "organization-user-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            ({"email": user.email, "id": user.id, "name": user.name} for user in users),
        )
