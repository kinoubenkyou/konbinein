from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.factories.personnel_factory import PersonnelFactory
from main.models.personnel import Personnel
from main.test_cases.user_test_case import UserTestCase


class PersonnelViewSetTestCase(UserTestCase):
    def test_agreeing(self):
        personnel = PersonnelFactory.create(user=self.user)
        path = reverse(
            "personnel-agreeing", kwargs={"pk": personnel.id, "user_id": self.user.id}
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(Personnel.objects.filter(id=personnel.id).get().does_user_agree)

    def test_create(self):
        path = reverse("personnel-list", kwargs={"user_id": self.user.id})
        organization = OrganizationFactory.create()
        data = {"organization": organization.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        actual = Personnel.objects.filter(**data).values().get()
        del actual["id"]
        self.assertEqual(
            actual,
            {
                "does_organization_agree": False,
                "does_user_agree": True,
                "organization_id": organization.id,
                "user_id": self.user.id,
            },
        )

    def test_destroy(self):
        personnel = PersonnelFactory.create(user=self.user)
        path = reverse(
            "personnel-detail", kwargs={"pk": personnel.id, "user_id": self.user.id}
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Personnel.objects.filter(id=personnel.id).exists(), False)

    def test_retrieve(self):
        personnel = PersonnelFactory.create(user=self.user)
        path = reverse(
            "personnel-detail", kwargs={"pk": personnel.id, "user_id": self.user.id}
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
