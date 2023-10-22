from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.authentications.token_authentication import TokenAuthentication
from main.factories.user_factory import UserFactory


class UserTestCase(APITestCase):
    is_organization_view_set = False
    is_user_system_administrator = False
    is_user_view_set = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(
            authentication_token=Token.generate_key(),
            is_system_administrator=cls.is_user_system_administrator,
        )

    def setUp(self):
        super().setUp()
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"{TokenAuthentication.SCHEME} {self.user.authentication_token}"
            )
        )
