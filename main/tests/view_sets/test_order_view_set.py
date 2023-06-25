from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.order_factory import OrderFactory
from main.factories.product_factory import ProductFactory
from main.factories.product_item_factory import ProductItemFactory
from main.models.order import Order
from main.models.product_item import ProductItem
from main.tests.staff_test_case import StaffTestCase


class OrderViewSetTestCase(StaffTestCase):
    def test_create(self):
        built_order = OrderFactory.build()
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_product_total = sum(
            built_product_item.total for built_product_item in built_product_items
        )
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "product_total": built_product_total,
            "productitem_set": [
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ],
            "total": built_product_total,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {**data, "organization_id": self.organization.id}
        product_item_data_list = filter_.pop("productitem_set")
        order = Order.objects.filter(**filter_).first()
        self.assertIsNotNone(order)
        for product_item_data in product_item_data_list:
            filter_ = {
                **product_item_data,
                "order_id": order.id,
                "total": product_item_data["price"] * product_item_data["quantity"],
            }
            self.assertTrue(ProductItem.objects.filter(**filter_).exists())

    def test_create__code_already_in_another_order(self):
        order = OrderFactory.create(organization=self.organization)
        built_order = OrderFactory.build(organization=self.organization)
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_product_total = sum(
            built_product_item.total for built_product_item in built_product_items
        )
        data = {
            "code": order.code,
            "created_at": built_order.created_at,
            "product_total": built_product_total,
            "productitem_set": [
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ],
            "total": built_product_total,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"code": ["Code is already in another order."]}
        )

    def test_create__product_in_another_organization(self):
        built_order = OrderFactory.build(organization=self.organization)
        products = ProductFactory.create_batch(2)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_product_total = sum(
            built_product_item.total for built_product_item in built_product_items
        )
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "product_total": built_product_total,
            "productitem_set": [
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ],
            "total": built_product_total,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {"product": ["Product is in another organization."]},
                    {"product": ["Product is in another organization."]},
                ]
            },
        )

    def test_create__product_total_incorrect(self):
        built_order = OrderFactory.build(organization=self.organization)
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_product_total = (
            sum(built_product_item.total for built_product_item in built_product_items)
            + 1
        )
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "product_total": built_product_total,
            "productitem_set": [
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ],
            "total": built_product_total,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"non_field_errors": ["Product total is incorrect."]}
        )

    def test_create__productitem_set_total_incorrect(self):
        built_order = OrderFactory.build(organization=self.organization)
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_product_total = sum(
            built_product_item.total for built_product_item in built_product_items
        )
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "product_total": built_product_total,
            "productitem_set": [
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total + 1,
                }
                for built_product_item in built_product_items
            ],
            "total": built_product_total,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {"non_field_errors": ["Total is incorrect."]}
                    for _ in range(len(built_product_items))
                ]
            },
        )

    def test_create__total_incorrect(self):
        built_order = OrderFactory.build(organization=self.organization)
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        built_product_total = sum(
            built_product_item.total for built_product_item in built_product_items
        )
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "product_total": built_product_total,
            "productitem_set": [
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ],
            "total": built_product_total + 1,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"non_field_errors": ["Total is incorrect."]})

    def test_destroy(self):
        order = OrderFactory.create(organization=self.organization)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())
        self.assertFalse(ProductItem.objects.filter(order_id=order.id).exists())

    def test_list__filter__code__in(self):
        OrderFactory.create(organization=self.organization)
        order_dicts = [
            {"object": order, "product_item_dicts": []}
            for order in OrderFactory.create_batch(2, organization=self.organization)
        ]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"code__in": [order_dict["object"].code for order_dict in order_dicts]}
        response = self.client.get(path, data, format="json")
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__created_at__gte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        orders.sort(key=lambda order: order.created_at, reverse=True)
        orders.pop()
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"created_at__gte": orders[-1].created_at}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__created_at__lte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        orders.sort(key=lambda order: order.created_at)
        orders.pop()
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"created_at__lte": orders[-1].created_at}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__product_total__gte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        orders.sort(key=lambda order: order.product_total, reverse=True)
        orders.pop()
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"product_total__gte": orders[-1].product_total}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__product_total__lte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        orders.sort(key=lambda order: order.product_total)
        orders.pop()
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"product_total__lte": orders[-1].product_total}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__productitem__name__in(self):
        order = OrderFactory.create(organization=self.organization)
        ProductItemFactory.create_batch(2, order=order)
        order_dicts = [
            {
                "object": order,
                "product_item_dicts": [
                    {"object": product_item}
                    for product_item in ProductItemFactory.create_batch(2, order=order)
                ],
            }
            for order in OrderFactory.create_batch(2, organization=self.organization)
        ]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "productitem__name__in": [
                product_item_dict["object"].name
                for order_dict in order_dicts
                for product_item_dict in order_dict["product_item_dicts"]
            ]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__total__gte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        orders.sort(key=lambda order: order.total, reverse=True)
        orders.pop()
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"total__gte": orders[-1].total}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__filter__total__lte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        orders.sort(key=lambda order: order.total)
        orders.pop()
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"total__lte": orders[-1].total}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, False)

    def test_list__paginate(self):
        orders = OrderFactory.create_batch(4, organization_id=self.organization.id)
        orders.sort(key=lambda order: order.id)
        order_dicts = [
            {"object": order, "product_item_dicts": []} for order in orders[1:3]
        ]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json()["results"], order_dicts, True)

    def test_list__sort__code(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        orders.sort(key=lambda order: order.code)
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, True)

    def test_list__sort__created_at(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        orders.sort(key=lambda order: order.created_at)
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "created_at"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, True)

    def test_list__sort__product_total(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        orders.sort(key=lambda order: order.product_total)
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(
            path, data={"ordering": "product_total"}, format="json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, True)

    def test_list__sort__total(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        orders.sort(key=lambda order: order.total)
        order_dicts = [{"object": order, "product_item_dicts": []} for order in orders]
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "total"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), order_dicts, True)

    def test_partial_update(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        built_order = OrderFactory.build()
        product_items = ProductItemFactory.create_batch(2, order=order)
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        built_product_total = sum(
            built_product_item.total for built_product_item in built_product_items
        )
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "productitem_set": (
                {
                    "id": product_items[0].id,
                    "name": built_product_items[0].name,
                    "product": built_product_items[0].product_id,
                    "quantity": built_product_items[0].quantity,
                    "price": built_product_items[0].price,
                    "total": built_product_items[0].total,
                },
                {
                    "name": built_product_items[1].name,
                    "product": built_product_items[1].product_id,
                    "quantity": built_product_items[1].quantity,
                    "price": built_product_items[1].price,
                    "total": built_product_items[1].total,
                },
            ),
            "product_total": built_product_total,
            "total": built_product_total,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = {**data, "id": order.id, "organization_id": self.organization.id}
        product_item_data_list = filter_.pop("productitem_set")
        self.assertTrue(Order.objects.filter(**filter_).exists())
        for product_item_data in product_item_data_list:
            filter_ = {
                **product_item_data,
                "order_id": order.id,
                "total": product_item_data["price"] * product_item_data["quantity"],
            }
            self.assertTrue(ProductItem.objects.filter(**filter_).exists())
        self.assertFalse(ProductItem.objects.filter(id=product_items[1].id).exists())

    def test_retrieve(self):
        order = OrderFactory.create(organization_id=self.organization.id)
        order_dicts = [
            {
                "object": order,
                "product_item_dicts": [
                    {"object": product_item}
                    for product_item in ProductItemFactory.create_batch(2, order=order)
                ],
            }
        ]
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response([response.json()], order_dicts, False)

    def _assert_get_response(self, order_data_list, order_dicts, is_ordered):
        if not is_ordered:
            order_data_list.sort(key=lambda order_data: order_data["id"])
            order_dicts.sort(key=lambda order_dict: order_dict["object"].id)
        self.assertEqual(
            [order_data["id"] for order_data in order_data_list],
            [order_dict["object"].id for order_dict in order_dicts],
        )
        for index, order_data in enumerate(order_data_list):
            product_item_data_list = order_data.pop("productitem_set")
            product_item_data_list.sort(
                key=lambda product_item_data: product_item_data["id"]
            )
            product_items = [
                product_item_dict["object"]
                for product_item_dict in order_dicts[index]["product_item_dicts"]
            ]
            product_items.sort(key=lambda product_item: product_item.id)
            expected = [
                {
                    "id": product_item.id,
                    "name": product_item.name,
                    "product": product_item.product_id,
                    "quantity": product_item.quantity,
                    "price": str(product_item.price),
                    "total": str(product_item.total),
                }
                for product_item in product_items
            ]
            self.assertEqual(product_item_data_list, expected)
        orders = [order_dict["object"] for order_dict in order_dicts]
        expected = [
            {
                "code": order.code,
                "created_at": order.created_at.isoformat(),
                "id": order.id,
                "product_total": str(order.product_total),
                "total": str(order.total),
            }
            for order in orders
        ]
        self.assertEqual(order_data_list, expected)
