from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.organization_factory import OrganizationFactory
from main.test_cases.user_test_case import UserTestCase


class UserOrganizationViewSetTestCase(UserTestCase):
    def test_list(self):
        organizations = OrganizationFactory.create_batch(2)
        path = reverse("user-organization-list", kwargs={"user_id": self.user.id})
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            (
                {
                    "code": organization.code,
                    "id": organization.id,
                    "name": organization.name,
                }
                for organization in organizations
            ),
        )
