from django.contrib.auth.hashers import check_password
from django.core import mail
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.test_cases.user_test_case import UserTestCase
from main.tests import faker


class UserViewSetTestCase(UserTestCase):
    def test_de_authenticating(self):
        path = reverse("user-de-authenticating", kwargs={"user_id": self.user.id})
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertIsNone(
            User.objects.filter(id=self.user.id).get().authentication_token
        )

    def test_destroy(self):
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(id=self.user.id).exists(), False)

    def test_partial_update(self):
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
        built_user = UserFactory.build()
        password = f"password{faker.unique.random_int()}"
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
            "current_password": self.user_current_password,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        actual = User.objects.filter(id=self.user.id).values().get()
        del actual["authentication_token"]
        del actual["id"]
        del actual["is_system_administrator"]
        email_verifying_token = actual.pop("email_verifying_token")
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
            "http://testserver/public/users/"
            f"{self.user.id}/email_verifying?token={email_verifying_token}"
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
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
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
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
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

    def test_retrieve(self):
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "email": self.user.email,
                "id": self.user.id,
                "name": self.user.name,
            },
        )
