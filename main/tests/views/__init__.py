from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.authentications.token_authentication import TokenAuthentication
from main.factories.user_factory import UserFactory


class TokenAuthenticatedTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        authentication_token = Token.generate_key()
        cls.user = UserFactory.create(authentication_token=authentication_token)

    def setUp(self):
        super().setUp()
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{TokenAuthentication.SCHEME} {self.user.authentication_token}"
            )
        )
