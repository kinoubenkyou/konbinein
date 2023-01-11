from django.urls import reverse
from faker import Faker
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
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
        url = reverse("order-list")
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
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_partial_update(self):
        order = OrderFactory.create()
        built_order = OrderFactory.build()
        built_order_items = OrderItemFactory.build_batch(2)
        order_items = OrderItemFactory.create_batch(2, order=order)
        organization = OrganizationFactory.create()
        url = reverse("order-detail", kwargs={"pk": order.id})
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
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)


class UserViewSetTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker_ = Faker()

    def test_create(self):
        built_user = UserFactory.build()
        url = reverse("user-list")
        data = {
            "email": built_user.email,
            "password": f"password{self.faker_.unique.random_int()}",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_partial_update(self):
        user = UserFactory.create()
        built_user = UserFactory.build()
        url = reverse("user-detail", kwargs={"pk": user.id})
        data = {
            "email": built_user.email,
            "password": f"password{self.faker_.unique.random_int()}",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
