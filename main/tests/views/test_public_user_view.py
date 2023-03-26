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
from rest_framework.test import APITestCase

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.tests import faker


class PublicUserViewSetTestCase(APITestCase):
    def test_authenticating(self):
        password = f"password{faker.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(password),
        )
        path = reverse("public-user-authenticating")
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
        user = UserFactory.create()
        path = reverse("public-user-authenticating")
        data = {
            "email": user.email,
            "password": f"password{faker.unique.random_int()}",
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Password is incorrect."])

    def test_create(self):
        path = reverse("public-user-list")
        built_user = UserFactory.build()
        password = f"password{faker.unique.random_int()}"
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {
            "authentication_token": None,
            "is_system_administrator": False,
        }
        del filter_["password"]
        user = User.objects.filter(**filter_).first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password(password, user.hashed_password))

        dict_ = mail.outbox[0].__dict__
        body = (
            f"http://testserver/public/users/{user.id}/email_verifying"
            f"?token={user.email_verifying_token}"
        )
        self.assertEqual(dict_["body"], body)
        self.assertEqual(dict_["from_email"], "webmaster@localhost")
        self.assertEqual(dict_["subject"], "Konbinein Email Verification")
        self.assertCountEqual(dict_["to"], (built_user.email,))

    def test_email_verifying(self):
        email_verifying_token = Token.generate_key()
        user = UserFactory.create(email_verifying_token=email_verifying_token)
        path = reverse("public-user-email-verifying", kwargs={"pk": user.id})
        data = {"token": email_verifying_token}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertIsNone(User.objects.filter(id=user.id).get().email_verifying_token)

    def test_email_verifying__token_not_match(self):
        email_verifying_token = Token.generate_key()
        user = UserFactory.create(email_verifying_token=email_verifying_token)
        path = reverse("public-user-email-verifying", kwargs={"pk": user.id})
        data = {"token": Token.generate_key()}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Token doesn't match."])

    def test_email_verifying__email_already_verified(self):
        user = UserFactory.create()
        path = reverse("public-user-email-verifying", kwargs={"pk": user.id})
        data = {"token": Token.generate_key()}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Email is already verified."])

    def test_partial_update(self):
        password_resetting_token = Token.generate_key()
        user = UserFactory.create(password_resetting_token=password_resetting_token)
        path = reverse("public-user-detail", kwargs={"pk": user.id})
        password = f"password{faker.unique.random_int()}"
        data = {"password": password, "token": password_resetting_token}
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        user = User.objects.filter(id=user.id, password_resetting_token=None).first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password(password, user.hashed_password))

    def test_partial_update__token_not_match(self):
        user = UserFactory.create(password_resetting_token=Token.generate_key())
        path = reverse("public-user-detail", kwargs={"pk": user.id})
        data = {
            "password": f"password{faker.unique.random_int()}",
            "token": Token.generate_key(),
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["Token doesn't match."]})

    def test_password_resetting(self):
        user = UserFactory.create()
        path = reverse("public-user-password-resetting")
        response = self.client.post(path, {"email": user.email}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        password_resetting_token = (
            User.objects.filter(id=user.id).get().password_resetting_token
        )
        self.assertIsNotNone(password_resetting_token)
        dict_ = mail.outbox[0].__dict__
        body = (
            "http://testserver/public/users/password_resetting"
            f"?token={password_resetting_token}"
        )
        self.assertEqual(dict_["body"], body)
        self.assertEqual(dict_["from_email"], "webmaster@localhost")
        self.assertEqual(dict_["subject"], "Konbinein Password Reset")
        self.assertCountEqual(dict_["to"], (user.email,))

    def test_password_resetting__email_not_verified(self):
        email_verifying_token = Token.generate_key()
        user = UserFactory.create(email_verifying_token=email_verifying_token)
        path = reverse("public-user-password-resetting")
        response = self.client.post(path, {"email": user.email}, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Email isn't verified."])
