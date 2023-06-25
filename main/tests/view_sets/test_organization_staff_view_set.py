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
from main.tests.staff_test_case import StaffTestCase


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
        data = {"user": UserFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {
            **data,
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
        response = self.client.post(path, data={"user": user.id}, format="json")
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
        self.assertFalse(Staff.objects.filter(id=staff.id).exists())

    def test_list__filter__does_organization_agree(self):
        StaffFactory.create(
            does_organization_agree=False, organization=self.organization
        )
        staffs = [
            StaffFactory.create(
                does_organization_agree=True, organization=self.organization
            ),
            self.staff,
        ]
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"does_organization_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, False)

    def test_list__filter__does_user_agree(self):
        StaffFactory.create(does_user_agree=False, organization=self.organization)
        staffs = [
            StaffFactory.create(does_user_agree=True, organization=self.organization),
            self.staff,
        ]
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"does_user_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, False)

    def test_list__filter__user_id__in(self):
        StaffFactory.create(organization=self.organization)
        staff_dicts = [
            {"object": staff}
            for staff in StaffFactory.create_batch(2, organization=self.organization)
        ]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "user_id__in": [staff_dict["object"].user_id for staff_dict in staff_dicts]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, False)

    def test_list__paginate(self):
        staffs = StaffFactory.create_batch(3, organization=self.organization)
        staffs.append(self.staff)
        staffs.sort(key=lambda staff: staff.id)
        staff_dicts = [{"object": staff} for staff in staffs[1:3]]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json()["results"], staff_dicts, True)

    def test_list__sort__does_organization_agree(self):
        staffs = [
            StaffFactory.create(
                does_organization_agree=False, organization=self.organization
            ),
            self.staff,
        ]
        staffs.sort(key=lambda staff: staff.does_organization_agree)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "does_organization_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, True)

    def test_list__sort__does_user_agree(self):
        staffs = [
            StaffFactory.create(does_user_agree=False, organization=self.organization),
            self.staff,
        ]
        staffs.sort(key=lambda staff: staff.does_user_agree)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "does_user_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, True)

    def test_list__sort__user__email(self):
        staffs = [StaffFactory.create(organization=self.organization), self.staff]
        staffs.sort(key=lambda staff: staff.user.email)
        staff_dicts = [{"object": staff} for staff in staffs]
        path = reverse(
            "organization-staff-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(
            path, data={"ordering": "user__email"}, format="json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), staff_dicts, True)

    def test_retrieve(self):
        staff_dicts = [{"object": self.staff}]
        path = reverse(
            "organization-staff-detail",
            kwargs={"organization_id": self.organization.id, "pk": self.staff.id},
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
                "user": staff.user_id,
                "user_email": staff.user.email,
            }
            for staff in staffs
        ]
        self.assertEqual(staff_data_list, expected)
