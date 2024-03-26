from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT

from main.factories.staff_factory import StaffFactory
from main.models.staff import Staff
from main.tests.view_sets.user_test_case import UserTestCase
from main.view_sets.user_staff_view_set import UserStaffViewSet


class UserStaffViewSetTestCase(UserTestCase):
    basename = "user-staff"
    query_set = Staff.objects.all()
    view_set = UserStaffViewSet

    def test_agreeing(self):
        staff = StaffFactory.create(user=self.user)
        path = reverse(
            "user-staff-agreeing", kwargs={"pk": staff.id, "user_id": self.user.id}
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertTrue(Staff.objects.filter(id=staff.id).get().does_user_agree)

    def test_create(self):
        data = self._get_deserializer_data()
        filter_ = {
            **data,
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": self.user.id,
        }
        self._act_and_assert_create_test(data, filter_)

    def test_create__staff_already_created(self):
        staff = StaffFactory.create(user=self.user)
        data = {**self._get_deserializer_data(), "organization": staff.organization.id}
        self._act_and_assert_create_validation_test(
            data, {"organization": ["Staff is already created."]}
        )

    def test_destroy(self):
        self._act_and_assert_destroy_test(StaffFactory.create(user=self.user))

    def test_list__filter__does_organization_agree(self):
        StaffFactory.create_batch(
            3, user=self.user, does_organization_agree=Iterator([True, True, False])
        )
        self._act_and_assert_list_test({"does_organization_agree": True})

    def test_list__filter__does_user_agree(self):
        StaffFactory.create_batch(
            3, user=self.user, does_user_agree=Iterator([True, True, False])
        )
        self._act_and_assert_list_test({"does_user_agree": True})

    def test_list__filter__organization__in(self):
        StaffFactory.create(user=self.user)
        staffs = StaffFactory.create_batch(2, user=self.user)
        self._act_and_assert_list_test({
            "organization__in": [staff.organization.id for staff in staffs]
        })

    def test_list__paginate(self):
        StaffFactory.create_batch(4, user=self.user)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__does_organization_agree(self):
        StaffFactory.create_batch(
            2, user=self.user, does_organization_agree=Iterator([True, False])
        )
        self._act_and_assert_list_test({"ordering": "does_organization_agree"})

    def test_list__sort__does_user_agree(self):
        StaffFactory.create_batch(
            2, user=self.user, does_user_agree=Iterator([True, False])
        )
        self._act_and_assert_list_test({"ordering": "does_organization_agree"})

    def test_list__sort__organization_code(self):
        StaffFactory.create_batch(2, user=self.user)
        self._act_and_assert_list_test({"ordering": "organization__code"})

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(StaffFactory.create(user=self.user).id)

    @staticmethod
    def _get_deserializer_data():
        staff = StaffFactory.build()
        staff.organization.save()
        return {"organization": staff.organization.id}

    @staticmethod
    def _get_serializer_data(staff):
        return {
            "does_organization_agree": staff.does_organization_agree,
            "does_user_agree": staff.does_user_agree,
            "id": staff.id,
            "organization": staff.organization_id,
            "organization_code": staff.organization.code,
        }
