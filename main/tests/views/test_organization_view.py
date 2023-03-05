from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.test_cases.system_administrator_test_case import SystemAdministratorTestCase


class OrganizationViewSetTestCase(SystemAdministratorTestCase):
    def test_create(self):
        built_organization = OrganizationFactory.build()
        path = reverse("organization-list")
        data = {"name": built_organization.name}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        id_ = response.json()["id"]
        organization = Organization.objects.get(id=id_)
        self.assertEqual(
            {key: getattr(organization, key) for key in data.keys()},
            data,
        )

    def test_destroy(self):
        organization = OrganizationFactory.create()
        path = reverse("organization-detail", kwargs={"pk": organization.id})
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(
            Organization.objects.filter(id=organization.id).exists(), False
        )

    def test_list(self):
        organizations = OrganizationFactory.create_batch(2)
        path = reverse("organization-list")
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            (
                {"id": organization.id, "name": organization.name}
                for organization in organizations
            ),
        )

    def test_partial_update(self):
        organization = OrganizationFactory.create()
        built_organization = OrganizationFactory.build()
        path = reverse("organization-detail", kwargs={"pk": organization.id})
        data = {"name": built_organization.name}
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        organization.refresh_from_db()
        self.assertEqual(
            {key: getattr(organization, key) for key in data.keys()},
            data,
        )

    def test_retrieve(self):
        organization = OrganizationFactory.create()
        path = reverse("organization-detail", kwargs={"pk": organization.id})
        response = self.client.patch(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            {"id": organization.id, "name": organization.name},
        )
