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
from main.test_cases.user_test_case import UserTestCase


class UserStaffViewSetTestCase(UserTestCase):
    def test_agreeing(self):
        staff = StaffFactory.create(user_id=self.user.id)
        path = reverse(
            "user-staff-agreeing", kwargs={"pk": staff.id, "user_id": self.user.id}
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(Staff.objects.filter(id=staff.id).get().does_user_agree)

    def test_create(self):
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        organization = OrganizationFactory.create()
        data = {"organization_id": organization.id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": self.user.id,
        }
        self.assertTrue(Staff.objects.filter(**filter_).exists())

    def test_create__staff_already_created(self):
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        organization = OrganizationFactory.create()
        data = {"organization_id": organization.id}
        StaffFactory.create(organization_id=organization.id, user_id=self.user.id)
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"organization_id": ["Staff is already created."]}
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
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"does_organization_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), staffs)

    def test_list__filter__does_user_agree(self):
        StaffFactory.create(does_user_agree=False, user=self.user)
        staffs = StaffFactory.create_batch(2, does_user_agree=True, user=self.user)
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"does_user_agree": True}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), staffs)

    def test_list__filter__organization_id__in(self):
        StaffFactory.create(user=self.user)
        staffs = StaffFactory.create_batch(2, user=self.user)
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"organization_id__in": tuple(staff.organization_id for staff in staffs)}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), staffs)

    def test_list__sort__does_organization_agree(self):
        does_organization_agree_list = (False, True)
        staffs = StaffFactory.create_batch(
            2,
            does_organization_agree=Iterator(does_organization_agree_list),
            user=self.user,
        )
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"ordering": "does_organization_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.does_organization_agree)
        self._assertGetResponseData(response.json(), staffs, is_ordered=True)

    def test_list__sort__does_user_agree(self):
        does_user_agree_list = (False, True)
        staffs = StaffFactory.create_batch(
            2, does_user_agree=Iterator(does_user_agree_list), user=self.user
        )
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"ordering": "does_user_agree"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.does_user_agree)
        self._assertGetResponseData(response.json(), staffs, is_ordered=True)

    def test_list__sort__organization_code(self):
        staffs = StaffFactory.create_batch(2, user=self.user)
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"ordering": "organization__code"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.organization.code)
        self._assertGetResponseData(response.json(), staffs, is_ordered=True)

    def test_list__paginate(self):
        staffs = StaffFactory.create_batch(4, user_id=self.user.id)
        path = reverse("user-staff-list", kwargs={"user_id": self.user.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        staffs.sort(key=lambda staff: staff.id)
        self._assertGetResponseData(
            response.json()["results"], (staffs[1], staffs[2]), is_ordered=True
        )

    def test_retrieve(self):
        staff = StaffFactory.create(user=self.user)
        path = reverse(
            "user-staff-detail", kwargs={"pk": staff.id, "user_id": self.user.id}
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
                "organization_code": staff.organization.code,
                "organization_id": staff.organization_id,
            }
            for staff in staffs
        ]
        if is_ordered:
            self.assertEqual(actual, expected)
        else:
            self.assertCountEqual(actual, expected)
