from django.test import TransactionTestCase
from django.test.client import RequestFactory
from rest_framework.exceptions import AuthenticationFailed

from main.authentications.token_authentication import TokenAuthentication


class TokenAuthenticationTestCase(TransactionTestCase):
    def test_authenticate__scheme_not_match(self):
        request = RequestFactory(HTTP_AUTHORIZATION="scheme").get("/")
        actual = TokenAuthentication().authenticate(request)
        self.assertIsNone(actual)

    def test_authenticate__token_not_provided(self):
        request = RequestFactory(HTTP_AUTHORIZATION=TokenAuthentication.SCHEME).get("/")
        with self.assertRaises(AuthenticationFailed):
            TokenAuthentication().authenticate(request)

    def test_authenticate__user_not_exist(self):
        from rest_framework.authtoken.models import Token

        http_authorization = f"{TokenAuthentication.SCHEME} {Token.generate_key()}"
        request = RequestFactory(HTTP_AUTHORIZATION=http_authorization).get("/")
        with self.assertRaises(AuthenticationFailed):
            TokenAuthentication().authenticate(request)
