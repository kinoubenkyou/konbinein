from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.models.organization import Organization
from main.tests.staff_test_case import StaffTestCase


class StaffOrganizationViewSetTestCase(StaffTestCase):
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
        data = {"code": built_organization.code, "name": built_organization.name}
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = {**data, "id": self.organization.id}
        self.assertTrue(Organization.objects.filter(**filter_).exists())

    def test_retrieve(self):
        path = reverse(
            "organization-detail", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(
            [response.json()], [{"object": self.organization}], False
        )

    def _assert_get_response(
        self, organization_data_list, organization_dicts, is_ordered
    ):
        if not is_ordered:
            organization_data_list.sort(
                key=lambda organization_data: organization_data["id"]
            )
            organization_dicts.sort(
                key=lambda organization_dict: organization_dict["object"].id
            )
        organizations = [
            organization_dict["object"] for organization_dict in organization_dicts
        ]
        expected = [
            {
                "code": organization.code,
                "id": organization.id,
                "name": organization.name,
            }
            for organization in organizations
        ]
        self.assertEqual(organization_data_list, expected)