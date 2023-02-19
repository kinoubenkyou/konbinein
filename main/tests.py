from django.contrib.auth.hashers import make_password
from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.urls import reverse
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.test import APITestCase

from main.authentications import TokenAuthentication
from main.factories import (
    OrderFactory,
    OrderItemFactory,
    OrganizationFactory,
    PersonnelFactory,
    UserFactory,
)


class AuthenticatedApiTestCase(APITestCase):
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


class OrderViewSetTestCase(AuthenticatedApiTestCase):
    def test_create(self):
        built_order = OrderFactory.build()
        built_order_items = OrderItemFactory.build_batch(2)
        organization = OrganizationFactory.create()
        path = reverse("order-list")
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "orderitem_set": (
                {
                    "name": order_item.name,
                    "quantity": order_item.quantity,
                    "unit_price": order_item.unit_price,
                }
                for order_item in built_order_items
            ),
            "organization": organization.id,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_partial_update(self):
        order = OrderFactory.create()
        built_order = OrderFactory.build()
        built_order_items = OrderItemFactory.build_batch(2)
        order_items = OrderItemFactory.create_batch(2, order=order)
        organization = OrganizationFactory.create()
        path = reverse("order-detail", kwargs={"pk": order.id})
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "orderitem_set": (
                {
                    "name": built_order_items[0].name,
                    "quantity": built_order_items[0].quantity,
                    "unit_price": built_order_items[0].unit_price,
                },
                {
                    "id": order_items[1].id,
                    "name": built_order_items[1].name,
                    "quantity": built_order_items[1].quantity,
                    "unit_price": built_order_items[1].unit_price,
                },
            ),
            "organization": organization.id,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)


class OrganizationPersonnelViewSetTestCase(AuthenticatedApiTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker_ = Faker()

    def test_create(self):
        organization = OrganizationFactory.create()
        PersonnelFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=organization,
            user=self.user,
        )
        path = reverse(
            "organization_personnel-list", kwargs={"organization_id": organization.id}
        )
        data = {"user": UserFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_post_agreeing(self):
        organization = OrganizationFactory.create()
        PersonnelFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=organization,
            user=self.user,
        )
        personnel = PersonnelFactory.create(organization=organization)
        path = reverse(
            "organization_personnel-agreeing",
            kwargs={"organization_id": organization.id, "pk": personnel.id},
        )
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


class PersonnelViewSetTestCase(AuthenticatedApiTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker_ = Faker()

    def test_create(self):
        path = reverse("personnel-list")
        data = {"organization": OrganizationFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_post_agreeing(self):
        personnel = PersonnelFactory.create(user=self.user)
        path = reverse("personnel-agreeing", kwargs={"pk": personnel.id})
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


class TokenAuthenticationTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker = Faker()

    def test_authenticate__header_not_provided(self):
        request = RequestFactory().get("/")
        second = TokenAuthentication().authenticate(request)
        self.assertEqual(None, second)

    def test_authenticate__scheme_not_match(self):
        request = RequestFactory(
            HTTP_AUTHORIZATION=f"scheme{self.faker.unique.random_int()}"
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
            f" authorization_token{self.faker.unique.random_int()}"
        )
        request = RequestFactory(HTTP_AUTHORIZATION=http_authorization).get("/")
        with self.assertRaises(AuthenticationFailed):
            TokenAuthentication().authenticate(request)


class UserViewSetTestCase(AuthenticatedApiTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker_ = Faker()

    def test_create(self):
        built_user = UserFactory.build()
        password = f"password{self.faker_.unique.random_int()}"
        path = reverse("user-list")
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_partial_update(self):
        current_password = f"password{self.faker_.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(current_password),
        )
        built_user = UserFactory.build()
        password = f"password{self.faker_.unique.random_int()}"
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
            "current_password": current_password,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_partial_update__current_password_required(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": f"password{self.faker_.unique.random_int()}",
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_partial_update__current_password_incorrect(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": f"password{self.faker_.unique.random_int()}",
            "current_password": "password",
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_authenticating(self):
        password = f"password{self.faker_.unique.random_int()}"
        user = UserFactory.create(
            hashed_password=make_password(password),
        )
        path = reverse("user-authenticating")
        data = {"email": user.email, "password": password}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_post_authenticating__password_incorrect(self):
        user = UserFactory.create()
        path = reverse("user-authenticating")
        data = {"email": user.email, "password": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_de_authenticating(self):
        path = reverse("user-de-authenticating")
        response = self.client.post(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_email_verifying(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": email_verification_token}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_email_verifying__token_not_match(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_email_verifying__email_already_verified(self):
        user = UserFactory.create()
        path = reverse("user-email-verifying", kwargs={"pk": user.id})
        data = {"token": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_password_resetting(self):
        user = UserFactory.create()
        path = reverse("user-password-resetting", kwargs={"pk": user.id})
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_password_resetting__email_not_verified(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-password-resetting", kwargs={"pk": user.id})
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
