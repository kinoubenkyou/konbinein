from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.order_factory import OrderFactory
from main.factories.order_item_factory import OrderItemFactory
from main.models.order import Order
from main.models.order_item import OrderItem
from main.test_cases.staff_test_case import StaffTestCase


class OrderViewSetTestCase(StaffTestCase):
    @staticmethod
    def _get_order_total(order_items):
        if len(order_items) == 0:
            return None
        order_total = sum(
            order_item.quantity * order_item.unit_price for order_item in order_items
        )
        return f"{order_total:.4f}"

    def test_create(self):
        built_order = OrderFactory.build()
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_order_items = OrderItemFactory.build_batch(2)
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
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {"organization_id": self.organization.id}
        del filter_["orderitem_set"]
        actual = Order.objects.filter(**filter_).values().get()
        order_id = actual.pop("id")
        expected = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "organization_id": self.organization.id,
        }
        self.assertEqual(actual, expected)
        actual = OrderItem.objects.filter(order_id=order_id).values()
        for dict_ in actual:
            del dict_["id"]
        expected = (
            {
                "name": built_order_items[0].name,
                "order_id": order_id,
                "quantity": built_order_items[0].quantity,
                "unit_price": built_order_items[0].unit_price,
            },
            {
                "name": built_order_items[1].name,
                "order_id": order_id,
                "quantity": built_order_items[1].quantity,
                "unit_price": built_order_items[1].unit_price,
            },
        )
        self.assertCountEqual(actual, expected)

    def test_destroy(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        OrderItemFactory.create(order=order)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.filter(id=order.id).exists(), False)
        self.assertEqual(OrderItem.objects.filter(order_id=order.id).exists(), False)

    def test_list(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(2, order=orders[0])
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        actual1 = response.json()
        actual2 = []
        for dict_ in actual1:
            actual2.extend(
                dict_.pop("orderitem_set"),
            )
        self.assertCountEqual(
            actual1,
            (
                {
                    "code": order.code,
                    "created_at": order.created_at.isoformat(),
                    "id": order.id,
                    "total": self._get_order_total(
                        tuple(
                            order_item
                            for order_item in order_items
                            if order_item.order_id == order.id
                        ),
                    ),
                }
                for order in orders
            ),
        )
        self.assertCountEqual(
            actual2,
            (
                {
                    "id": order_item.id,
                    "name": order_item.name,
                    "quantity": order_item.quantity,
                    "unit_price": f"{order_item.unit_price:.4f}",
                    "total": f"{order_item.quantity * order_item.unit_price:.4f}",
                }
                for order_item in order_items
            ),
        )

    def test_partial_update(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        built_order = OrderFactory.build()
        built_order_items = OrderItemFactory.build_batch(2)
        order_items = OrderItemFactory.create_batch(2, order=order)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
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
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        actual = Order.objects.filter(id=order.id).values().get()
        order_id = actual.pop("id")
        expected = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "organization_id": self.organization.id,
        }
        self.assertEqual(actual, expected)
        actual = OrderItem.objects.filter(order_id=order_id).values()
        for dict_ in actual:
            del dict_["id"]
        expected = (
            {
                "name": built_order_items[0].name,
                "order_id": order_id,
                "quantity": built_order_items[0].quantity,
                "unit_price": built_order_items[0].unit_price,
            },
            {
                "name": built_order_items[1].name,
                "order_id": order_id,
                "quantity": built_order_items[1].quantity,
                "unit_price": built_order_items[1].unit_price,
            },
        )
        self.assertCountEqual(actual, expected)

    def test_retrieve(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(2, order=order)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        actual1 = response.json()
        actual2 = actual1.pop("orderitem_set")
        self.assertEqual(
            actual1,
            {
                "code": order.code,
                "created_at": order.created_at.isoformat(),
                "id": order.id,
                "total": self._get_order_total(order_items),
            },
        )
        self.assertCountEqual(
            actual2,
            (
                {
                    "id": order_item.id,
                    "name": order_item.name,
                    "quantity": order_item.quantity,
                    "unit_price": f"{order_item.unit_price:.4f}",
                    "total": f"{order_item.quantity * order_item.unit_price:.4f}",
                }
                for order_item in order_items
            ),
        )
