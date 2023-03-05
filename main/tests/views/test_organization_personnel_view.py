from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.personnel_factory import PersonnelFactory
from main.factories.user_factory import UserFactory
from main.test_cases.organization_user_test_case import OrganizationUserTestCase


class OrganizationPersonnelViewSetTestCase(OrganizationUserTestCase):
    def test_create(self):
        path = reverse(
            "organization_personnel-list",
            kwargs={"organization_id": self.organization.id},
        )
        data = {"user": UserFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_post_agreeing(self):
        personnel = PersonnelFactory.create(organization=self.organization)
        path = reverse(
            "organization_personnel-agreeing",
            kwargs={"organization_id": self.organization.id, "pk": personnel.id},
        )
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
