from rest_framework.test import APITestCase

from main.authentications.token_authentication import TokenAuthentication
from main.factories.user_factory import UserFactory
from main.shortcuts import get_authentication_token, set_authentication_token


class UserTestCase(APITestCase):
    is_user_system_administrator = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserFactory.create(
            is_system_administrator=cls.is_user_system_administrator,
        )
        set_authentication_token(user.id)
        cls.user = user

    def setUp(self):
        super().setUp()
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{TokenAuthentication.SCHEME} {get_authentication_token(self.user.id)}"
            )
        )
