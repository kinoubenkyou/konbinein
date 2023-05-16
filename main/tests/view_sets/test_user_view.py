from django.contrib.auth.hashers import check_password
from django.core import mail
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from main.factories.user_factory import UserFactory
from main.models.user import User
from main.test_cases.user_test_case import UserTestCase


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
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_partial_update(self):
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
        built_user = UserFactory.build()
        password = "password"
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
            "current_password": self.user_current_password,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = {**data, "id": self.user.id}
        del filter_["password"]
        del filter_["current_password"]
        user = User.objects.filter(**filter_).first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password(password, user.hashed_password))
        dict_ = mail.outbox[0].__dict__
        body = (
            f"http://testserver/public/users/{self.user.id}/email_verifying"
            f"?token={user.email_verifying_token}"
        )
        self.assertEqual(dict_["body"], body)
        self.assertEqual(dict_["from_email"], "webmaster@localhost")
        self.assertEqual(dict_["subject"], "Konbinein Email Verification")
        self.assertCountEqual(dict_["to"], (built_user.email,))

    def test_partial_update__current_password_required(self):
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"user_id": self.user.id})
        data = {
            "email": built_user.email,
            "password": "password",
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
            "password": "password",
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
