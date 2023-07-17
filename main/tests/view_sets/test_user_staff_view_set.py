from factory import Iterator
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
from main.tests.user_test_case import UserTestCase


class UserStaffViewSetTestCase(UserTestCase):
    def test_agreeing(self):
        staff = StaffFactory.create(user=self.user)
        path = reverse(
            "user-staff-agreeing", kwargs={"pk": staff.id, "user_id": self.user.id}
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(Staff.objects.filter(id=staff.id).get().does_user_agree)

    def test_create(self):
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        organization = OrganizationFactory.create()
        data = {"organization": organization.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {
            **data,
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": self.user.id,
        }
        self.assertTrue(Staff.objects.filter(**filter_).exists())

    def test_create__staff_already_created(self):
        organization = OrganizationFactory.create()
        StaffFactory.create(organization=organization, user=self.user)
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"organization": organization.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"organization": ["Staff is already created."]}
        )

    def test_destroy(self):
        staff = StaffFactory.create(user=self.user)
        path = reverse(
            "user-staff-detail", kwargs={"pk": staff.id, "user_id": self.user.id}
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Staff.objects.filter(id=staff.id).exists())

    def test_list__filter__does_organization_agree(self):
        StaffFactory.create(does_organization_agree=False, user=self.user)
        staffs = StaffFactory.create_batch(
            2, does_organization_agree=True, user=self.user
        )
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"does_organization_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, False)

    def test_list__filter__does_user_agree(self):
        StaffFactory.create(does_user_agree=False, user=self.user)
        staffs = StaffFactory.create_batch(2, does_user_agree=True, user=self.user)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"does_user_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, False)

    def test_list__filter__organization__in(self):
        StaffFactory.create(user=self.user)
        staffs = StaffFactory.create_batch(2, user=self.user)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"organization__in": [staff.organization_id for staff in staffs]}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, False)

    def test_list__paginate(self):
        staffs = StaffFactory.create_batch(4, user_id=self.user.id)
        staffs.sort(key=lambda staff: staff.id)
        staff_dicts = [{"object": staff} for staff in staffs[1:3]]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json()["results"], staff_dicts, True)

    def test_list__sort__does_organization_agree(self):
        staffs = StaffFactory.create_batch(
            2,
            does_organization_agree=Iterator([False, True]),
            user=self.user,
        )
        staffs.sort(key=lambda staff: staff.does_organization_agree)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"ordering": "does_organization_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, True)

    def test_list__sort__does_user_agree(self):
        staffs = StaffFactory.create_batch(
            2,
            does_user_agree=Iterator([False, True]),
            user=self.user,
        )
        staffs.sort(key=lambda staff: staff.does_user_agree)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"ordering": "does_user_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, True)

    def test_list__sort__organization_code(self):
        staffs = StaffFactory.create_batch(2, user=self.user)
        staffs.sort(key=lambda staff: staff.organization.code)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"ordering": "organization__code"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, True)

    def test_retrieve(self):
        staff = StaffFactory.create(user=self.user)
        staff_dicts = [{"object": staff}]
        path = reverse(
            "user-staff-detail", kwargs={"pk": staff.id, "user_id": self.user.id}
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response([response.json()], staff_dicts, False)

    def _assert_get_response(self, staff_data_list, staff_dicts, is_ordered):
        if not is_ordered:
            staff_data_list.sort(key=lambda staff_data: staff_data["id"])
            staff_dicts.sort(key=lambda staff_dict: staff_dict["object"].id)
        staffs = [staff_dict["object"] for staff_dict in staff_dicts]
        expected = [
            {
                "does_organization_agree": staff.does_organization_agree,
                "does_user_agree": staff.does_user_agree,
                "id": staff.id,
                "organization": staff.organization_id,
                "organization_code": staff.organization.code,
            }
            for staff in staffs
        ]
        self.assertEqual(staff_data_list, expected)
