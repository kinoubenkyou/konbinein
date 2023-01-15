from django.urls import reverse
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.test import APITestCase

from main.factories import (
    OrderFactory,
    OrderItemFactory,
    OrganizationFactory,
    UserFactory,
)


class OrderViewSetTestCase(APITestCase):
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


class UserViewSetTestCase(APITestCase):
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
            "password_confirmation": password,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create__password_not_match_confirmation(self):
        built_user = UserFactory.build()
        path = reverse("user-list")
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": f"password{self.faker_.unique.random_int()}",
            "password_confirmation": "password",
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        password = f"password{self.faker_.unique.random_int()}"
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": password,
            "password_confirmation": password,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_partial_update__password_not_match_confirmation(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        path = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "name": built_user.name,
            "password": f"password{self.faker_.unique.random_int()}",
            "password_confirmation": "password",
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_email_verification(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verification", kwargs={"pk": user.id})
        data = {"token": email_verification_token}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_post_email_verification__token_not_match(self):
        email_verification_token = Token.generate_key()
        user = UserFactory.create(email_verification_token=email_verification_token)
        path = reverse("user-email-verification", kwargs={"pk": user.id})
        data = {"token": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_post_email_verification__email_already_verified(self):
        user = UserFactory.create()
        path = reverse("user-email-verification", kwargs={"pk": user.id})
        data = {"token": ""}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
