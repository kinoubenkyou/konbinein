from secrets import token_urlsafe

from django.contrib.auth.hashers import check_password
from django.test import override_settings
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.shortcuts import (
    get_authentication_token,
    get_email_verifying_token,
    get_password_resetting_token,
    set_email_verifying_token,
    set_password_resetting_token,
)
from main.tests.view_sets.view_set_test_case import ViewSetTestCase
from main.view_sets.public_user_view_set import PublicUserViewSet


class PublicUserViewSetTestCase(ViewSetTestCase):
    basename = "public-user"
    view_set = PublicUserViewSet

    def test_authenticating(self):
        user = UserFactory.create()
        path = reverse("public-user-authenticating")
        data = {"email": user.email, "password": user.password}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        authentication_token = get_authentication_token(user.id)
        self.assertEqual(
            response.json(),
            {"user_id": user.id, "token": authentication_token},
        )
        self.assertIsNotNone(authentication_token)

    def test_authenticating__password_incorrect(self):
        data = {"email": UserFactory.create().email, "password": "password"}
        self._act_and_assert_action_validation_test(
            "authenticating", data, ["Password is incorrect."], None
        )

    @override_settings(task_always_eager=True)
    def test_create(self):
        data = self._get_deserializer_data()
        filter_ = {**data, "is_system_administrator": False}
        self._act_and_assert_create_test(data, filter_)
        user = User.objects.filter(**filter_).first()
        body = (
            f"http://testserver/public/users/{user.id}/email_verifying"
            f"?token={get_email_verifying_token(user.id)}"
        )
        self._assert_email(body, "Konbinein Email Verification", [user.email])

    def test_email_verifying(self):
        user = UserFactory.create()
        set_email_verifying_token(user.id)
        data = {"token": get_email_verifying_token(user.id)}
        self._act_and_assert_action_response_status("email-verifying", data, user.id)
        self.assertIsNone(get_email_verifying_token(user.id))

    def test_email_verifying__token_not_match(self):
        user = UserFactory.create()
        set_email_verifying_token(user.id)
        data = {"token": token_urlsafe()}
        self._act_and_assert_action_validation_test(
            "email-verifying",
            data,
            ["Token doesn't match."],
            user.id,
        )

    def test_email_verifying__email_already_verified(self):
        data = {"token": token_urlsafe()}
        self._act_and_assert_action_validation_test(
            "email-verifying",
            data,
            ["Email is already verified."],
            UserFactory.create().id,
        )

    @override_settings(task_always_eager=True)
    def test_password_resetting(self):
        user = UserFactory.create()
        set_password_resetting_token(user.id)
        data = {"email": user.email}
        self._act_and_assert_action_response_status("password-resetting", data, None)
        body = (
            "http://testserver/public/users/password_resetting"
            f"?token={get_password_resetting_token(user.id)}"
        )
        self._assert_email(body, "Konbinein Password Reset", [user.email])

    def test_password_resetting__email_not_verified(self):
        user = UserFactory.create()
        set_email_verifying_token(user.id)
        data = {"email": user.email}
        self._act_and_assert_action_validation_test(
            "password-resetting",
            data,
            ["Email isn't verified."],
            None,
        )

    def test_update(self):
        password = "password"
        user = UserFactory.create()
        set_password_resetting_token(user.id)
        data = {"password": password, "token": get_password_resetting_token(user.id)}
        filter_ = {"password": password}
        self._act_and_assert_update_test(data, filter_, user.id)
        self.assertIsNone(get_password_resetting_token(user.id))

    def test_update__token_not_match(self):
        user = UserFactory.create()
        data = {"password": "password", "token": token_urlsafe()}
        self._act_and_assert_update_validation_test(
            data,
            {"token": ["Token doesn't match."]},
            user.id,
        )

    def _assert_and_get_saved_object(self, data, filter_):
        password = filter_.pop("password")
        users = list(self._get_query_set().filter(**filter_))
        self.assertEqual(len(users), 1)
        self.assertTrue(check_password(password, users[0].hashed_password))
        return users[0]

    @staticmethod
    def _get_deserializer_data():
        user = UserFactory.build()
        return {"email": user.email, "name": user.name, "password": user.password}

    def _get_query_set(self):
        return User.objects.all()
