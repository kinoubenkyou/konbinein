from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.organization_factory import OrganizationFactory
from main.factories.staff_factory import StaffFactory
from main.models.staff import Staff
from main.test_cases.user_test_case import UserTestCase


class StaffViewSetTestCase(UserTestCase):
    def test_agreeing(self):
        staff = StaffFactory.create(user_id=self.user.id)
        path = reverse(
            "staff-agreeing", kwargs={"pk": staff.id, "user_id": self.user.id}
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(Staff.objects.filter(id=staff.id).get().does_user_agree)

    def test_create(self):
        path = reverse("staff-list", kwargs={"user_id": self.user.id})
        organization = OrganizationFactory.create()
        data = {"organization": organization.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        actual = Staff.objects.filter(**data).values().get()
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

    def test_create__staff_already_created(self):
        path = reverse("staff-list", kwargs={"user_id": self.user.id})
        organization = OrganizationFactory.create()
        data = {"organization": organization.id}
        StaffFactory.create(organization_id=organization.id, user_id=self.user.id)
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"organization": ["Staff is already created."]}
        )

    def test_destroy(self):
        staff = StaffFactory.create(user=self.user)
        path = reverse("staff-detail", kwargs={"pk": staff.id, "user_id": self.user.id})
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Staff.objects.filter(id=staff.id).exists(), False)

    def test_list(self):
        staffs = StaffFactory.create_batch(2, user_id=self.user.id)
        path = reverse("staff-list", kwargs={"user_id": self.user.id})
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            (
                {
                    "does_organization_agree": staff.does_organization_agree,
                    "does_user_agree": staff.does_user_agree,
                    "id": staff.id,
                    "organization": staff.organization_id,
                    "user": staff.user_id,
                }
                for staff in staffs
            ),
        )

    def test_retrieve(self):
        staff = StaffFactory.create(user=self.user)
        path = reverse("staff-detail", kwargs={"pk": staff.id, "user_id": self.user.id})
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "does_organization_agree": staff.does_organization_agree,
                "does_user_agree": staff.does_user_agree,
                "id": staff.id,
                "organization": staff.organization_id,
                "user": staff.user_id,
            },
        )
