from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED

from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.models.staff import Staff
from main.test_cases.admin_test_case import AdminTestCase


class AdminOrganizationViewSetTestCase(AdminTestCase):
    def test_create(self):
        path = reverse("admin-organization-list")
        built_organization = OrganizationFactory.build()
        data = {
            "code": built_organization.code,
            "name": built_organization.name,
            "user_id": self.user.id,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {**data}
        del filter_["user_id"]
        organization = Organization.objects.filter(**filter_).first()
        self.assertIsNotNone(organization)
        self.assertTrue(
            Staff.objects.filter(
                organization=organization.id, user=self.user.id
            ).exists()
        )
