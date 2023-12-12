from django.core.cache import cache
from rest_framework.test import APITestCase

from main.authentications.token_authentication import BearerAuthentication
from main.factories.user_factory import UserFactory
from main.shortcuts import get_authentication_token, set_authentication_token


class UserTestCase(APITestCase):
    is_user_system_administrator = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(
            is_system_administrator=cls.is_user_system_administrator,
        )

    def setUp(self):
        super().setUp()
        set_authentication_token(self.user.id)
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{BearerAuthentication.SCHEME} {self.user.id}"
                f" {get_authentication_token(self.user.id)}"
            )
        )

    def tearDown(self):
        cache.clear()
