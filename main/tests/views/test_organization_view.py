from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.test_cases.organization_user_test_case import OrganizationUserTestCase


class OrganizationViewSetTestCase(OrganizationUserTestCase):
    def test_destroy(self):
        path = reverse(
            "organization-detail", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(
            Organization.objects.filter(id=self.organization.id).exists(), False
        )

    def test_partial_update(self):
        path = reverse(
            "organization-detail", kwargs={"organization_id": self.organization.id}
        )
        built_organization = OrganizationFactory.build()
        data = {"name": built_organization.name}
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        actual = Organization.objects.filter(id=self.organization.id).values().get()
        del actual["id"]
        self.assertEqual(actual, {"name": built_organization.name})

    def test_retrieve(self):
        path = reverse(
            "organization-detail", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"id": self.organization.id, "name": self.organization.name},
        )
