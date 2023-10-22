from django.contrib.auth.hashers import check_password
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.tests.public_test_case import PublicTestCase
from main.tests.view_sets.view_set_mixin import ViewSetTestCaseMixin


class PublicUserViewSetTestCase(ViewSetTestCaseMixin, PublicTestCase):
    basename = "public-user"
    model = User

    def test_authenticating(self):
        user = UserFactory.create()
        path = reverse("public-user-authenticating")
        data = {"email": user.email, "password": user.password}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        authentication_token = (
            User.objects.filter(id=user.id).get().authentication_token
        )
        self.assertEqual(
            response.json(),
            {"token": authentication_token},
        )
        self.assertIsNotNone(authentication_token)

    def test_authenticating__password_incorrect(self):
        data = {"email": UserFactory.create().email, "password": "password"}
        self._act_and_assert_action_validation_test(
            "authenticating", data, ["Password is incorrect."], None
        )

    @override_settings(task_always_eager=True)
    def test_create(self):
        data = self._deserializer_data()
        filter_ = {
            **data,
            "authentication_token": None,
            "is_system_administrator": False,
        }
        self._act_and_assert_create_test(data, filter_)
        user = User.objects.filter(**filter_).first()
        body = (
            f"http://testserver/public/users/{user.id}/email_verifying"
            f"?token={user.email_verifying_token}"
        )
        self._assert_email(body, "Konbinein Email Verification", [user.email])

    def test_email_verifying(self):
        email_verifying_token = Token.generate_key()
        user = UserFactory.create(email_verifying_token=email_verifying_token)
        path = reverse("public-user-email-verifying", kwargs={"pk": user.id})
        data = {"token": email_verifying_token}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertIsNone(User.objects.filter(id=user.id).get().email_verifying_token)

    def test_email_verifying__token_not_match(self):
        data = {"token": Token.generate_key()}
        self._act_and_assert_action_validation_test(
            "email-verifying",
            data,
            ["Token doesn't match."],
            UserFactory.create(email_verifying_token=Token.generate_key()).id,
        )

    def test_email_verifying__email_already_verified(self):
        data = {"token": Token.generate_key()}
        self._act_and_assert_action_validation_test(
            "email-verifying",
            data,
            ["Email is already verified."],
            UserFactory.create().id,
        )

    def test_partial_update(self):
        password = "password"
        password_resetting_token = Token.generate_key()
        data = {"password": password, "token": password_resetting_token}
        user = UserFactory.create(password_resetting_token=password_resetting_token)
        filter_ = {"password": password, "password_resetting_token": None}
        self._act_and_assert_partial_update_test(data, filter_, user.id)

    def test_partial_update__token_not_match(self):
        data = {"password": "password", "token": Token.generate_key()}
        user = UserFactory.create(password_resetting_token=Token.generate_key())
        self._act_and_assert_partial_update_validation_test(
            data,
            {"token": ["Token doesn't match."]},
            user.id,
        )

    @override_settings(task_always_eager=True)
    def test_password_resetting(self):
        user = UserFactory.create()
        path = reverse("public-user-password-resetting")
        data = {"email": user.email}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        password_resetting_token = (
            User.objects.filter(id=user.id).get().password_resetting_token
        )
        self.assertIsNotNone(password_resetting_token)
        body = (
            "http://testserver/public/users/password_resetting"
            f"?token={password_resetting_token}"
        )
        self._assert_email(body, "Konbinein Password Reset", [user.email])

    def test_password_resetting__email_not_verified(self):
        data = {
            "email": UserFactory.create(
                email_verifying_token=Token.generate_key()
            ).email
        }
        self._act_and_assert_action_validation_test(
            "password-resetting",
            data,
            ["Email isn't verified."],
            None,
        )

    def _assert_saved_object(self, filter_):
        password = filter_.pop("password")
        user = User.objects.filter(**filter_).first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password(password, user.hashed_password))

    @staticmethod
    def _deserializer_data():
        user = UserFactory.build()
        return {"email": user.email, "name": user.name, "password": user.password}
