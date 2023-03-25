from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.staff_factory import StaffFactory
from main.factories.user_factory import UserFactory
from main.models.staff import Staff
from main.test_cases.staff_test_case import StaffTestCase


class OrganizationStaffViewSetTestCase(StaffTestCase):
    def test_agreeing(self):
        staff = StaffFactory.create(organization=self.organization)
        path = reverse(
            "organization-staff-agreeing",
            kwargs={"organization_id": self.organization.id, "pk": staff.id},
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(Staff.objects.filter(id=staff.id).get().does_organization_agree)

    def test_create(self):
        path = reverse(
            "organization-staff-list",
            kwargs={"organization_id": self.organization.id},
        )
        user = UserFactory.create()
        data = {"user": user.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        actual = Staff.objects.filter(**data).values().get()
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

    def test_create__staff_already_created(self):
        path = reverse(
            "organization-staff-list",
            kwargs={"organization_id": self.organization.id},
        )
        user = UserFactory.create()
        data = {"user": user.id}
        StaffFactory.create(organization_id=self.organization.id, user_id=user.id)
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"user": ["Staff is already created."]})

    def test_destroy(self):
        staff = StaffFactory.create(organization=self.organization)
        path = reverse(
            "organization-staff-detail",
            kwargs={"organization_id": self.organization.id, "pk": staff.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Staff.objects.filter(id=staff.id).exists(), False)

    def test_list(self):
        staffs = StaffFactory.create_batch(1, organization=self.organization)
        authenticated_staff = self.user.staff_set.get()
        staffs.append(authenticated_staff)
        path = reverse(
            "organization-staff-list",
            kwargs={"organization_id": self.organization.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json(),
            (
                {
                    "does_organization_agree": staffs[0].does_organization_agree,
                    "does_user_agree": staffs[0].does_user_agree,
                    "id": staffs[0].id,
                    "organization": staffs[0].organization_id,
                    "user": staffs[0].user_id,
                },
                {
                    "does_organization_agree": staffs[1].does_organization_agree,
                    "does_user_agree": staffs[1].does_user_agree,
                    "id": staffs[1].id,
                    "organization": staffs[1].organization_id,
                    "user": staffs[1].user_id,
                },
            ),
        )

    def test_retrieve(self):
        staff = StaffFactory.create(organization=self.organization)
        path = reverse(
            "organization-staff-detail",
            kwargs={"organization_id": self.organization.id, "pk": staff.id},
        )
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
