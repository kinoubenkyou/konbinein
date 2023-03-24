from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED

from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.models.personnel import Personnel
from main.test_cases.admin_test_case import AdminTestCase


class AdminOrganizationViewSetTestCase(AdminTestCase):
    def test_create(self):
        path = reverse("admin-organization-list")
        built_organization = OrganizationFactory.build()
        data = {"name": built_organization.name, "user": self.user.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        actual = (
            Organization.objects.filter(**{"name": built_organization.name})
            .values()
            .get()
        )
        id_ = actual.pop("id")
        self.assertEqual(actual, {"name": built_organization.name})
        self.assertTrue(
            Personnel.objects.filter(organization=id_, user=self.user.id).exists()
        )
