from django.test import TransactionTestCase
from django.test.client import RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from main.authentications.token_authentication import BearerAuthentication


class BearerAuthenticationTestCase(TransactionTestCase):
    def test_authenticate__scheme_not_match(self):
        request = RequestFactory(
            HTTP_AUTHORIZATION=f"{BearerAuthentication.SCHEME}_"
        ).get(None)
        self.assertIsNone(BearerAuthentication().authenticate(request))

    def test_authenticate__no_user_id(self):
        request = RequestFactory(HTTP_AUTHORIZATION=BearerAuthentication.SCHEME).get(
            None
        )
        with self.assertRaises(AuthenticationFailed):
            BearerAuthentication().authenticate(request)

    def test_authenticate__no_token(self):
        request = RequestFactory(
            HTTP_AUTHORIZATION=f"{BearerAuthentication.SCHEME} 0"
        ).get(None)
        with self.assertRaises(AuthenticationFailed):
            BearerAuthentication().authenticate(request)

    def test_authenticate__token_not_match(self):
        http_authorization = f"{BearerAuthentication.SCHEME} 0 {Token.generate_key()}"
        request = RequestFactory(HTTP_AUTHORIZATION=http_authorization).get(None)
        with self.assertRaises(AuthenticationFailed):
            BearerAuthentication().authenticate(request)
