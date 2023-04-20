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
        data = {"user_id": UserFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {
            "does_organization_agree": True,
            "does_user_agree": False,
            "organization_id": self.organization.id,
        }
        self.assertTrue(Staff.objects.filter(**filter_).exists())

    def test_create__staff_already_created(self):
        user = UserFactory.create()
        StaffFactory.create(organization=self.organization, user=user)
        path = reverse(
            "organization-staff-list",
            kwargs={"organization_id": self.organization.id},
        )
        response = self.client.post(path, data={"user_id": user.id}, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"user_id": ["Staff is already created."]})

    def test_destroy(self):
        staff = StaffFactory.create(organization=self.organization)
        path = reverse(
            "organization-staff-detail",
            kwargs={"organization_id": self.organization.id, "pk": staff.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Staff.objects.filter(id=staff.id).exists())

    def test_list__filter__does_organization_agree(self):
        staffs = (
            StaffFactory.create(
                does_organization_agree=True, organization=self.organization
            ),
            self.staff,
        )
        StaffFactory.create(
            does_organization_agree=False, organization=self.organization
        )
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"does_organization_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), staffs)

    def test_list__filter__does_user_agree(self):
        staffs = (
            StaffFactory.create(does_user_agree=True, organization=self.organization),
            self.staff,
        )
        StaffFactory.create(does_user_agree=False, organization=self.organization)
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"does_user_agree": True}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), staffs)

    def test_list__filter__user_id__in(self):
        staffs = StaffFactory.create_batch(2, organization=self.organization)
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"user_id__in": tuple(staff.user_id for staff in staffs)}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), staffs)

    def test_list__paginate(self):
        staffs = StaffFactory.create_batch(3, organization=self.organization)
        staffs.append(self.staff)
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.id)
        self._assertGetResponseData(
            response.json()["results"], (staffs[1], staffs[2]), is_ordered=True
        )

    def test_list__sort__does_organization_agree(self):
        staffs = [
            StaffFactory.create(
                does_organization_agree=False, organization=self.organization
            ),
            self.staff,
        ]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "does_organization_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.does_organization_agree)
        self._assertGetResponseData(response.json(), staffs, is_ordered=True)

    def test_list__sort__does_user_agree(self):
        staffs = [
            StaffFactory.create(does_user_agree=False, organization=self.organization),
            self.staff,
        ]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "does_user_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.does_user_agree)
        self._assertGetResponseData(response.json(), staffs, is_ordered=True)

    def test_list__sort__user_email(self):
        staffs = [StaffFactory.create(organization=self.organization), self.staff]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "user__email"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.user.email)
        self._assertGetResponseData(response.json(), staffs, is_ordered=True)

    def test_retrieve(self):
        staff = StaffFactory.create(organization=self.organization)
        path = reverse(
            "organization-staff-detail",
            kwargs={"organization_id": self.organization.id, "pk": staff.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            (response.json(),),
            (staff,),
        )

    def _assertGetResponseData(self, actual, staffs, is_ordered=False):
        expected = [
            {
                "does_organization_agree": staff.does_organization_agree,
                "does_user_agree": staff.does_user_agree,
                "id": staff.id,
                "user_id": staff.user_id,
                "user_email": staff.user.email,
            }
            for staff in staffs
        ]
        if is_ordered:
            self.assertEqual(actual, expected)
        else:
            self.assertCountEqual(actual, expected)
