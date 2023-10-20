from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.authentications.token_authentication import TokenAuthentication
from main.factories.user_factory import UserFactory
from main.tests import faker


class UserTestCase(APITestCase):
    is_organization_view_set = False
    is_user_system_administrator = False
    is_user_view_set = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_current_password = f"password{faker.unique.random_int()}"
        cls.user = UserFactory.create(
            authentication_token=Token.generate_key(),
            hashed_password=make_password(cls.user_current_password),
            is_system_administrator=cls.is_user_system_administrator,
        )

    def setUp(self):
        super().setUp()
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{TokenAuthentication.SCHEME} {self.user.authentication_token}"
            )
        )
