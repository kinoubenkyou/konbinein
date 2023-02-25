from django.test import TransactionTestCase
from django.test.client import RequestFactory
from rest_framework.exceptions import AuthenticationFailed

from main.authentications.token_authentication import TokenAuthentication
from main.tests import faker


class TokenAuthenticationTestCase(TransactionTestCase):
    def test_authenticate__header_not_provided(self):
        request = RequestFactory().get("/")
        second = TokenAuthentication().authenticate(request)
        self.assertEqual(None, second)

    def test_authenticate__scheme_not_match(self):
        request = RequestFactory(
            HTTP_AUTHORIZATION=f"scheme{faker.unique.random_int()}"
        ).get("/")
        second = TokenAuthentication().authenticate(request)
        self.assertEqual(None, second)

    def test_authenticate__token_not_provided(self):
        request = RequestFactory(HTTP_AUTHORIZATION=TokenAuthentication.SCHEME).get("/")
        with self.assertRaises(AuthenticationFailed):
            TokenAuthentication().authenticate(request)

    def test_authenticate__user_not_exist(self):
        http_authorization = (
            f"{TokenAuthentication.SCHEME}"
            f" authorization_token{faker.unique.random_int()}"
        )
        request = RequestFactory(HTTP_AUTHORIZATION=http_authorization).get("/")
        with self.assertRaises(AuthenticationFailed):
            TokenAuthentication().authenticate(request)
