from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from main.factories.order_factory import OrderFactory
from main.factories.order_item_factory import OrderItemFactory
from main.factories.organization_factory import OrganizationFactory
from main.tests.views import TokenAuthenticatedTestCase


class OrderViewSetTestCase(TokenAuthenticatedTestCase):
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
