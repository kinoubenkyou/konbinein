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
from main.tests import faker
from main.tests.staff_test_case import StaffTestCase


class OrderViewSetTestCase(StaffTestCase):
    def test_create(self):
        built_order = OrderFactory.build()
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "productitem_set": tuple(
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ),
            "total": sum(
                built_product_item.price * built_product_item.quantity
                for built_product_item in built_product_items
            ),
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
        data = {
            "code": order.code,
            "created_at": built_order.created_at,
            "productitem_set": tuple(
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ),
            "total": sum(
                built_product_item.price * built_product_item.quantity
                for built_product_item in built_product_items
            ),
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
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "productitem_set": tuple(
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ),
            "total": sum(
                built_product_item.price * built_product_item.quantity
                for built_product_item in built_product_items
            ),
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

    def test_create__productitem_set_total_incorrect(self):
        built_order = OrderFactory.build(organization=self.organization)
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        built_product_items = ProductItemFactory.build_batch(
            2, product=Iterator(products)
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "productitem_set": tuple(
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total + 1,
                }
                for built_product_item in built_product_items
            ),
            "total": sum(
                built_product_item.price * built_product_item.quantity
                for built_product_item in built_product_items
            ),
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
        data = {
            "code": built_order.code,
            "created_at": built_order.created_at,
            "productitem_set": tuple(
                {
                    "name": built_product_item.name,
                    "product": built_product_item.product_id,
                    "quantity": built_product_item.quantity,
                    "price": built_product_item.price,
                    "total": built_product_item.total,
                }
                for built_product_item in built_product_items
            ),
            "total": sum(
                built_product_item.price * built_product_item.quantity
                for built_product_item in built_product_items
            )
            + 1,
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
        orders = OrderFactory.create_batch(2, organization=self.organization)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"code__in": tuple(order.code for order in orders)}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders)

    def test_list__filter__created_at__gte(self):
        created_at_list = [faker.past_datetime() for _ in range(3)]
        created_at_list.sort(reverse=True)
        OrderFactory.create(
            organization=self.organization, created_at=created_at_list.pop()
        )
        orders = OrderFactory.create_batch(
            2,
            organization=self.organization,
            created_at=Iterator(created_at_list),
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"created_at__gte": orders[-1].created_at}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders)

    def test_list__filter__created_at__lte(self):
        created_at_list = [faker.past_datetime() for _ in range(3)]
        created_at_list.sort()
        OrderFactory.create(
            organization=self.organization, created_at=created_at_list.pop()
        )
        orders = OrderFactory.create_batch(
            2,
            organization=self.organization,
            created_at=Iterator(created_at_list),
        )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"created_at__lte": orders[-1].created_at}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), orders)

    def test_list__filter__productitem__name__in(self):
        order = OrderFactory.create(organization=self.organization)
        ProductItemFactory.create_batch(2, order=order)
        orders = OrderFactory.create_batch(2, organization=self.organization)
        product_item_dict = {}
        for filtered_order in orders:
            product_item_dict[filtered_order.id] = ProductItemFactory.create_batch(
                2, order=filtered_order
            )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "productitem__name__in": tuple(
                product_items[0].name for _, product_items in product_item_dict.items()
            )
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(), orders, product_item_dict=product_item_dict
        )

    def test_list__filter__total__gte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        product_items = ProductItemFactory.create_batch(6, order=Iterator(orders))
        orders.sort(key=lambda order_: order_.total, reverse=True)
        orders.pop()
        product_item_dict = {}
        for order in orders:
            product_item_dict[order.id] = tuple(
                product_item
                for product_item in product_items
                if product_item.order_id == order.id
            )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"total__gte": orders[-1].total}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(), orders, product_item_dict=product_item_dict
        )

    def test_list__filter__total__lte(self):
        orders = OrderFactory.create_batch(3, organization=self.organization)
        product_items = ProductItemFactory.create_batch(6, order=Iterator(orders))
        orders.sort(key=lambda order_: order_.total)
        orders.pop()
        product_item_dict = {}
        for order in orders:
            product_item_dict[order.id] = tuple(
                product_item
                for product_item in product_items
                if product_item.order_id == order.id
            )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"total__lte": orders[-1].total}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(), orders, product_item_dict=product_item_dict
        )

    def test_list__paginate(self):
        orders = OrderFactory.create_batch(4, organization_id=self.organization.id)
        orders.sort(key=lambda order: order.id)
        paginated_orders = (orders[1], orders[2])
        product_item_dict = {}
        for order in paginated_orders:
            product_item_dict[order.id] = ProductItemFactory.create_batch(
                2, order=order
            )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json()["results"],
            paginated_orders,
            is_ordered=True,
            product_item_dict=product_item_dict,
        )

    def test_list__sort__code(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        orders.sort(key=lambda order: order.code)
        self._assertGetResponseData(response.json(), orders, is_ordered=True)

    def test_list__sort__created_at(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "created_at"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        orders.sort(key=lambda order: order.created_at)
        self._assertGetResponseData(response.json(), orders, is_ordered=True)

    def test_list__sort__total(self):
        orders = OrderFactory.create_batch(2, organization_id=self.organization.id)
        product_item_dict = {}
        for order in orders:
            product_item_dict[order.id] = ProductItemFactory.create_batch(
                2, order=order
            )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "total"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        orders.sort(key=lambda order: order.total)
        self._assertGetResponseData(
            response.json(),
            orders,
            is_ordered=True,
            product_item_dict=product_item_dict,
        )

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
            "total": sum(
                product_item.price * product_item.quantity
                for product_item in built_product_items
            ),
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
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        product_items = ProductItemFactory.create_batch(
            2, order=order, product=Iterator(products)
        )
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            (response.json(),),
            (order,),
            product_items,
        )

    def _assertGetResponseData(
        self, actual1, orders, is_ordered=False, product_item_dict=None
    ):
        actual2 = {dict_["id"]: dict_.pop("productitem_set") for dict_ in actual1}
        expected = [
            {
                "code": order.code,
                "created_at": order.created_at.isoformat(),
                "id": order.id,
                "total": str(order.total),
            }
            for order in orders
        ]
        if is_ordered:
            self.assertSequenceEqual(actual1, expected)
        else:
            self.assertCountEqual(actual1, expected)
        if product_item_dict is not None:
            self.assertCountEqual(
                tuple(id_ for id_ in actual2), tuple(id_ for id_ in product_item_dict)
            )
            for id_, product_item_data_list in actual2.items():
                self.assertCountEqual(
                    product_item_data_list,
                    (
                        {
                            "id": product_item.id,
                            "name": product_item.name,
                            "product": product_item.product_id,
                            "quantity": product_item.quantity,
                            "price": str(product_item.price),
                            "total": str(product_item.total),
                        }
                        for product_item in product_item_dict[id_]
                    ),
                )
