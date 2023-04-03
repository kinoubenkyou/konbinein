from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.order_factory import OrderFactory
from main.factories.order_item_factory import OrderItemFactory
from main.models.order import Order
from main.models.order_item import OrderItem
from main.test_cases.staff_test_case import StaffTestCase
from main.tests import faker


class OrderViewSetTestCase(StaffTestCase):
    def _assertGetResponseData(self, actual1, orders, order_items, is_ordered=False):
        actual2 = []
        for dict_ in actual1:
            actual2.extend(
                dict_.pop("orderitem_set"),
            )
        expected = [
            {
                "code": order.code,
                "created_at": order.created_at.isoformat(),
                "id": order.id,
                "total": f"{self._get_order_total(order, order_items):.4f}",
            }
            for order in orders
        ]
        if is_ordered:
            self.assertEqual(actual1, expected)
        else:
            self.assertCountEqual(actual1, expected)
        self.assertCountEqual(
            actual2,
            (
                {
                    "id": order_item.id,
                    "name": order_item.name,
                    "quantity": order_item.quantity,
                    "price": f"{order_item.price:.4f}",
                    "total": f"{order_item.quantity * order_item.price:.4f}",
                }
                for order_item in order_items
            ),
        )

    @staticmethod
    def _get_order_total(order, order_items):
        return sum(
            order_item.quantity * order_item.price
            for order_item in (
                order_item
                for order_item in order_items
                if order_item.order_id == order.id
            )
        )

    def test_create(self):
        built_order = OrderFactory.build()
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_order_items = OrderItemFactory.build_batch(2)
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "orderitem_set": tuple(
                {
                    "name": order_item.name,
                    "quantity": order_item.quantity,
                    "price": order_item.price,
                }
                for order_item in built_order_items
            ),
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {"organization_id": self.organization.id}
        order_item_data_list = filter_.pop("orderitem_set")
        order = Order.objects.filter(**filter_).first()
        self.assertIsNotNone(order)
        for order_item_data in order_item_data_list:
            filter_ = order_item_data | {"order_id": order.id}
            self.assertTrue(OrderItem.objects.filter(**filter_).exists())

    def test_destroy(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        OrderItemFactory.create(order=order)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())
        self.assertFalse(OrderItem.objects.filter(order_id=order.id).exists())

    def test_list(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders, order_items)

    def test_list__filter__code__in(self):
        OrderFactory.create(organization_id=self.organization.id)
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"code__in": tuple(order.code for order in orders)}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders, order_items)

    def test_list__filter__created_at__gte(self):
        created_at_list = [faker.past_datetime() for _ in range(3)]
        created_at_list.sort(reverse=True)
        OrderFactory.create(
            organization_id=self.organization.id, created_at=created_at_list.pop()
        )
        orders = OrderFactory.create_batch(
            2,
            organization_id=self.organization.id,
            created_at=Iterator(created_at_list),
        )
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"created_at__gte": orders[-1].created_at}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders, order_items)

    def test_list__filter__created_at__lte(self):
        created_at_list = [faker.past_datetime() for _ in range(3)]
        created_at_list.sort()
        OrderFactory.create(
            organization_id=self.organization.id, created_at=created_at_list.pop()
        )
        orders = OrderFactory.create_batch(
            2,
            organization_id=self.organization.id,
            created_at=Iterator(created_at_list),
        )
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"created_at__lte": orders[-1].created_at}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders, order_items)

    def test_list__filter__orderitem__name__in(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        OrderItemFactory.create_batch(2, order=order)
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "orderitem__name__in": tuple(order_item.name for order_item in order_items)
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders, order_items)

    def test_list__ordering__code(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "code"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(),
            sorted(orders, key=lambda order: order.code),
            order_items,
            is_ordered=True,
        )

    def test_list__ordering__created_at(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "created_at"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(),
            sorted(orders, key=lambda order: order.created_at),
            order_items,
            is_ordered=True,
        )

    def test_list__ordering__total(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(4, order=Iterator(orders))
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "total"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(),
            sorted(orders, key=lambda order: self._get_order_total(order, order_items)),
            order_items,
            is_ordered=True,
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
                    "price": built_order_items[0].price,
                },
                {
                    "id": order_items[0].id,
                    "name": built_order_items[1].name,
                    "quantity": built_order_items[1].quantity,
                    "price": built_order_items[1].price,
                },
            ),
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = data | {"id": order.id, "organization_id": self.organization.id}
        order_item_data_list = filter_.pop("orderitem_set")
        self.assertTrue(Order.objects.filter(**filter_).exists())
        for order_item_data in order_item_data_list:
            filter_ = order_item_data | {"order_id": order.id}
            self.assertTrue(OrderItem.objects.filter(**filter_).exists())
        self.assertFalse(OrderItem.objects.filter(id=order_items[1].id).exists())

    def test_retrieve(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        order_items = OrderItemFactory.create_batch(2, order=order)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            (response.json(),),
            (order,),
            order_items,
        )
