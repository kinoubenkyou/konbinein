from django.contrib.auth.hashers import check_password
from django.test import override_settings
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.shortcuts import (
    get_authentication_token,
    get_email_verifying_token,
    set_email_verifying_token,
)
from main.tests.user_test_case import UserTestCase
from main.tests.view_sets.user_view_set_test_case_mixin import UserViewSetTestCaseMixin


class UserViewSetTestCase(UserViewSetTestCaseMixin, UserTestCase):
    basename = "user"
    model = User

    def test_de_authenticating(self):
        path = reverse(
            "user-de-authenticating",
            kwargs={"pk": self.user.id, "user_id": self.user.id},
        )
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertIsNone(get_authentication_token(self.user.id))

    def test_destroy(self):
        self._act_and_assert_destroy_test(self.user.id)

    @override_settings(task_always_eager=True)
    def test_partial_update(self):
        set_email_verifying_token(self.user.id)
        data = {
            **self._deserializer_data(),
            "current_password": self.user.password,
            "password": "password",
        }
        filter_ = {**data}
        del filter_["current_password"]
        self._act_and_assert_partial_update_test(data, filter_, self.user.id)
        del filter_["password"]
        user = User.objects.filter(**filter_).first()
        body = (
            f"http://testserver/public/users/{user.id}/email_verifying"
            f"?token={get_email_verifying_token(user.id)}"
        )
        self._assert_email(body, "Konbinein Email Verification", [user.email])

    def test_partial_update__current_password_required(self):
        data = {**self._deserializer_data(), "password": "password"}
        self._act_and_assert_partial_update_validation_test(
            data,
            {
                "email": ["Current password is required."],
                "password": ["Current password is required."],
            },
            self.user.id,
        )

    def test_partial_update__current_password_incorrect(self):
        data = {
            **self._deserializer_data(),
            "current_password": "password",
            "password": "password",
        }
        self._act_and_assert_partial_update_validation_test(
            data, {"current_password": ["Current password is incorrect."]}, self.user.id
        )

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(self.user.id)

    def _assert_saved_object(self, filter_):
        password = filter_.pop("password")
        user = User.objects.filter(**filter_).first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password(password, user.hashed_password))

    @staticmethod
    def _deserializer_data():
        user = UserFactory.build()
        return {"email": user.email, "name": user.name}

    @staticmethod
    def _serializer_data(user):
        return {"email": user.email, "id": user.id, "name": user.name}
