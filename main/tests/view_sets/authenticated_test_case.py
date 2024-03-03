from main.authentications.token_authentication import BearerAuthentication
from main.factories.user_factory import UserFactory
from main.shortcuts import get_authentication_token, set_authentication_token
from main.tests.view_sets.view_set_test_case import ViewSetTestCase


class AuthenticatedTestCase(ViewSetTestCase):
    is_user_system_administrator = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(
            is_system_administrator=cls.is_user_system_administrator,
        )

    def setUp(self):
        super().setUp()
        set_authentication_token(self.user.id)
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{BearerAuthentication.SCHEME} {self.user.id}"
                f" {get_authentication_token(self.user.id)}"
            )
        )

    def _act_and_assert_create_test(self, data, filter_):
        super()._act_and_assert_create_test(data, filter_)
        object_id = self.view_set.queryset.filter(**filter_).first().id
        self._assert_saved_activity("create", data, object_id)

    def _act_and_assert_destroy_test(self, object_):
        super()._act_and_assert_destroy_test(object_)
        self._assert_saved_activity("destroy", {}, object_.id)

    def _act_and_assert_update_test(self, data, filter_, pk):
        super()._act_and_assert_update_test(data, filter_, pk)
        self._assert_saved_activity("update", data, pk)

    def _assert_saved_activity(self, action, data, object_id):
        activities = self.view_set.activity_class.objects(
            action=action,
            object_id=object_id,
            user_id=self.user.id,
            user_name=self.user.name,
            **data,
        )
        self.assertEqual(len(activities), 1)
