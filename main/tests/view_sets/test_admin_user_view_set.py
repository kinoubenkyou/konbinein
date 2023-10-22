from factory import Iterator

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.tests.admin_test_case import AdminTestCase
from main.tests.view_sets.view_set_mixin import ViewSetTestCaseMixin


class AdminUserViewSetTestCase(ViewSetTestCaseMixin, AdminTestCase):
    basename = "admin-user"
    model = User

    def test_list__filter__email__icontains(self):
        UserFactory.create()
        UserFactory.create_batch(
            2, email=Iterator(range(2), getter=lambda n: f"-email--{n}@email.com")
        )
        self._act_and_assert_list_test({"email__icontains": "email--"})

    def test_list__filter__name__icontains(self):
        UserFactory.create()
        UserFactory.create_batch(
            2, name=Iterator(range(2), getter=lambda n: f"-name--{n}")
        )
        self._act_and_assert_list_test({"name__icontains": "name--"})

    def test_list__paginate(self):
        UserFactory.create_batch(4)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__email(self):
        UserFactory.create_batch(2)
        self._act_and_assert_list_test({"ordering": "email"})

    def test_list__sort__name(self):
        UserFactory.create_batch(2)
        self._act_and_assert_list_test({"ordering": "name"})

    @staticmethod
    def _serializer_data(user):
        return {"email": user.email, "id": user.id, "name": user.name}
