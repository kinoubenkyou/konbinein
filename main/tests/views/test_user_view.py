from django.contrib.auth.hashers import check_password, make_password
from django.core import mail
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.test_cases.user_test_case import UserTestCase
from main.tests import faker


class UserViewSetTestCase(UserTestCase):
    def test_authenticating(self):
        self.client.credentials()
        password = f"password{faker.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(password),
        )
        path = reverse("user-authenticating")
        data = {"email": user.email, "password": password}
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
        self.client.credentials()
        user = UserFactory.create()
        path = reverse("user-authenticating")
        data = {
            "email": user.email,
            "password": f"password{faker.unique.random_int()}",
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Password is incorrect."])

    def test_create(self):
        self.client.credentials()
        path = reverse("user-list")
        built_user = UserFactory.build()
        password = f"password{faker.unique.random_int()}"
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {}
        del filter_["password"]
        actual = User.objects.filter(**filter_).values().get()
        del actual["email_verification_token"]
        del actual["id"]
        hashed_password = actual.pop("hashed_password")
        self.assertEqual(
            actual,
            {
                "authentication_token": None,
                "email": built_user.email,
                "is_system_administrator": False,
                "name": built_user.name,
            },
        )
        self.assertTrue(check_password(password, hashed_password))

    def test_de_authenticating(self):
        path = reverse("user-de-authenticating")
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertIsNone(
            User.objects.filter(id=self.user.id).get().authentication_token
        )

    def test_email_verifying(self):
        self.client.credentials()
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": email_verification_token}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertIsNone(
            User.objects.filter(id=user.id).get().email_verification_token
        )

    def test_email_verifying__token_not_match(self):
        self.client.credentials()
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": Token.generate_key()}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Token doesn't match."])

    def test_email_verifying__email_already_verified(self):
        self.client.credentials()
        user = UserFactory.create()
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": Token.generate_key()}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Email is already verified."])

    def test_partial_update(self):
        current_password = f"password{faker.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(current_password),
        )
        path = reverse("user-detail", kwargs={"pk": user.id})
        built_user = UserFactory.build()
        password = f"password{faker.unique.random_int()}"
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
            "current_password": current_password,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        actual = User.objects.filter(id=user.id).values().get()
        del actual["authentication_token"]
        del actual["id"]
        del actual["is_system_administrator"]
        email_verification_token = actual.pop("email_verification_token")
        hashed_password = actual.pop("hashed_password")
        self.assertEqual(
            actual,
            {"email": built_user.email, "name": built_user.name},
        )
        self.assertTrue(check_password(password, hashed_password))
        dict_ = mail.outbox[0].__dict__
        actual = {
            key: dict_[key]
            for key in dict_
            if key in ("body", "from_email", "subject", "to")
        }
        body = (
            "http://testserver/users/"
            f"{user.id}/email_verifying?token={email_verification_token}"
        )
        self.assertEqual(
            actual,
            {
                "body": body,
                "from_email": "webmaster@localhost",
                "subject": "Konbinein Email Verification",
                "to": [built_user.email],
            },
        )

    def test_partial_update__current_password_required(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "password": f"password{faker.unique.random_int()}",
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "email": ["Current password is required."],
                "password": ["Current password is required."],
            },
        )

    def test_partial_update__current_password_incorrect(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": f"password{faker.unique.random_int()}",
            "current_password": "password",
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"current_password": ["Current password is incorrect."]}
        )

    def test_password_resetting(self):
        self.client.credentials()
        user = UserFactory.create()
        path = reverse("user-password-resetting")
        response = self.client.post(path, {"email": user.email}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        dict_ = mail.outbox[0].__dict__
        actual = {
            key: dict_[key] for key in dict_ if key in ("from_email", "subject", "to")
        }
        self.assertTrue(
            check_password(
                dict_["body"], User.objects.filter(id=user.id).get().hashed_password
            )
        )
        self.assertEqual(
            actual,
            {
                "from_email": "webmaster@localhost",
                "subject": "Konbinein Password Reset",
                "to": [user.email],
            },
        )

    def test_password_resetting__email_not_verified(self):
        self.client.credentials()
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-password-resetting")
        response = self.client.post(path, {"email": user.email}, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Email isn't verified."])
