from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.test_cases.staff_test_case import StaffTestCase


class OrganizationViewSetTestCase(StaffTestCase):
    def test_destroy(self):
        path = reverse(
            "organization-detail", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Organization.objects.filter(id=self.organization.id).exists())

    def test_partial_update(self):
        path = reverse(
            "organization-detail", kwargs={"organization_id": self.organization.id}
        )
        built_organization = OrganizationFactory.build()
        data = {"name": built_organization.name}
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = data | {"id": self.organization.id}
        self.assertTrue(Organization.objects.filter(**filter_).exists())

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
