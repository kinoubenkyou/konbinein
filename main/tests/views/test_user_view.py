from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.user_factory import UserFactory
from main.test_cases.token_authenticated_test_case import TokenAuthenticatedTestCase
from main.tests import faker


class UserViewSetTestCase(TokenAuthenticatedTestCase):
    def test_create(self):
        built_user = UserFactory.build()
        password = f"password{faker.unique.random_int()}"
        path = reverse("user-list")
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_partial_update(self):
        current_password = f"password{faker.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(current_password),
        )
        built_user = UserFactory.build()
        password = f"password{faker.unique.random_int()}"
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
            "current_password": current_password,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_partial_update__current_password_required(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": f"password{faker.unique.random_int()}",
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

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

    def test_post_authenticating(self):
        password = f"password{faker.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(password),
        )
        path = reverse("user-authenticating")
        data = {"email": user.email, "password": password}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_post_authenticating__password_incorrect(self):
        user = UserFactory.create()
        path = reverse("user-authenticating")
        data = {"email": user.email, "password": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_de_authenticating(self):
        path = reverse("user-de-authenticating")
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_email_verifying(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": email_verification_token}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_email_verifying__token_not_match(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_email_verifying__email_already_verified(self):
        user = UserFactory.create()
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_password_resetting(self):
        user = UserFactory.create()
        path = reverse("user-password-resetting", kwargs={"pk": user.id})
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_password_resetting__email_not_verified(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-password-resetting", kwargs={"pk": user.id})
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
