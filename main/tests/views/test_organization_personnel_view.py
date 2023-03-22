from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.personnel_factory import PersonnelFactory
from main.factories.user_factory import UserFactory
from main.models.personnel import Personnel
from main.test_cases.organization_user_test_case import OrganizationUserTestCase


class OrganizationPersonnelViewSetTestCase(OrganizationUserTestCase):
    def test_agreeing(self):
        personnel = PersonnelFactory.create(organization=self.organization)
        path = reverse(
            "organization_personnel-agreeing",
            kwargs={"organization_id": self.organization.id, "pk": personnel.id},
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(
            Personnel.objects.filter(id=personnel.id).get().does_organization_agree
        )

    def test_create(self):
        path = reverse(
            "organization_personnel-list",
            kwargs={"organization_id": self.organization.id},
        )
        user = UserFactory.create()
        data = {"user": user.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        actual = Personnel.objects.filter(**data).values().get()
        del actual["id"]
        self.assertEqual(
            actual,
            {
                "does_organization_agree": True,
                "does_user_agree": False,
                "organization_id": self.organization.id,
                "user_id": user.id,
            },
        )

    def test_destroy(self):
        personnel = PersonnelFactory.create(organization=self.organization)
        path = reverse(
            "organization_personnel-detail",
            kwargs={"organization_id": self.organization.id, "pk": personnel.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Personnel.objects.filter(id=personnel.id).exists(), False)

    def test_list(self):
        personnels = PersonnelFactory.create_batch(1, organization=self.organization)
        authenticated_personnel = self.user.personnel_set.get()
        personnels.append(authenticated_personnel)
        path = reverse(
            "organization_personnel-list",
            kwargs={"organization_id": self.organization.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            (
                {
                    "does_organization_agree": personnels[0].does_organization_agree,
                    "does_user_agree": personnels[0].does_user_agree,
                    "id": personnels[0].id,
                    "organization": personnels[0].organization_id,
                    "user": personnels[0].user_id,
                },
                {
                    "does_organization_agree": personnels[1].does_organization_agree,
                    "does_user_agree": personnels[1].does_user_agree,
                    "id": personnels[1].id,
                    "organization": personnels[1].organization_id,
                    "user": personnels[1].user_id,
                },
            ),
        )

    def test_retrieve(self):
        personnel = PersonnelFactory.create(organization=self.organization)
        path = reverse(
            "organization_personnel-detail",
            kwargs={"organization_id": self.organization.id, "pk": personnel.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "does_organization_agree": personnel.does_organization_agree,
                "does_user_agree": personnel.does_user_agree,
                "id": personnel.id,
                "organization": personnel.organization_id,
                "user": personnel.user_id,
            },
        )
