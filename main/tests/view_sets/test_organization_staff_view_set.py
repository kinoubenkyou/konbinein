from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT

from main.factories.staff_factory import StaffFactory
from main.models.staff import Staff
from main.tests.view_sets.organization_test_case import OrganizationTestCase
from main.view_sets.organization_staff_view_set import OrganizationStaffViewSet


class OrganizationStaffViewSetTestCase(OrganizationTestCase):
    basename = "organization-staff"
    view_set = OrganizationStaffViewSet

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
        data = self._get_deserializer_data()
        filter_ = {
            **data,
            "does_organization_agree": True,
            "does_user_agree": False,
            "organization_id": self.organization.id,
        }
        self._act_and_assert_create_test(data, filter_)

    def test_create__staff_already_created(self):
        staff = StaffFactory.create(organization=self.organization)
        data = {**self._get_deserializer_data(), "user": staff.user.id}
        self._act_and_assert_create_validation_test(
            data, {"user": ["Staff is already created."]}
        )

    def test_destroy(self):
        self._act_and_assert_destroy_test(
            StaffFactory.create(organization=self.organization)
        )

    def test_list__filter__does_organization_agree(self):
        StaffFactory.create_batch(
            3,
            organization=self.organization,
            does_organization_agree=Iterator([True, True, False]),
        )
        self._act_and_assert_list_test({"does_organization_agree": True})

    def test_list__filter__does_user_agree(self):
        StaffFactory.create_batch(
            3,
            organization=self.organization,
            does_user_agree=Iterator([True, True, False]),
        )
        self._act_and_assert_list_test({"does_user_agree": True})

    def test_list__filter__user__in(self):
        StaffFactory.create(organization=self.organization)
        staffs = StaffFactory.create_batch(2, organization=self.organization)
        self._act_and_assert_list_test({
            "user__in": [staff.user.id for staff in staffs]
        })

    def test_list__paginate(self):
        StaffFactory.create_batch(4, organization=self.organization)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__does_organization_agree(self):
        StaffFactory.create_batch(
            2,
            organization=self.organization,
            does_organization_agree=Iterator([True, False]),
        )
        self._act_and_assert_list_test({"ordering": "does_organization_agree"})

    def test_list__sort__does_user_agree(self):
        StaffFactory.create_batch(
            2, organization=self.organization, does_user_agree=Iterator([True, False])
        )
        self._act_and_assert_list_test({"ordering": "does_user_agree"})

    def test_list__sort__user__email(self):
        StaffFactory.create_batch(2, organization=self.organization)
        self._act_and_assert_list_test({"ordering": "user__email"})

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(
            StaffFactory.create(organization=self.organization).id
        )

    @staticmethod
    def _get_deserializer_data():
        staff = StaffFactory.build()
        staff.user.save()
        return {"user": staff.user.id}

    @staticmethod
    def _get_serializer_data(staff):
        return {
            "does_organization_agree": staff.does_organization_agree,
            "does_user_agree": staff.does_user_agree,
            "id": staff.id,
            "user": staff.user_id,
            "user_email": staff.user.email,
        }
