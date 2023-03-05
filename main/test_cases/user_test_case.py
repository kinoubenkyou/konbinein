from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.authentications.token_authentication import TokenAuthentication
from main.factories.user_factory import UserFactory


class UserTestCase(APITestCase):
    is_user_system_administrator = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        authentication_token = Token.generate_key()
        cls.user = UserFactory.create(
            authentication_token=authentication_token,
            is_system_administrator=cls.is_user_system_administrator,
        )

    def setUp(self):
        super().setUp()
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{TokenAuthentication.SCHEME} {self.user.authentication_token}"
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
