from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.order_with_related_factory import OrderWithRelatedFactory
from main.factories.product_factory import ProductFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.models.order import Order
from main.models.product_item import ProductItem
from main.models.product_shipping_item import ProductShippingItem
from main.tests.staff_test_case import StaffTestCase


class OrderViewSetTestCaseMixin:
    @classmethod
    def _get_expected_data_list(cls, kwargs):
        filter_ = {
            key: value
            for key, value in kwargs.items()
            if key not in ["limit", "offset", "ordering"]
        }
        order_query_set = Order.objects.filter(**filter_)
        if "ordering" in kwargs:
            order_query_set = order_query_set.order_by(kwargs["ordering"])
        offset = kwargs.get("offset", 0)
        return [
            {
                "code": order.code,
                "created_at": order.created_at.isoformat(),
                "id": order.id,
                "productitem_set": [
                    cls._get_product_item_data(product_item)
                    for product_item in order.productitem_set.order_by("id")
                ],
                "product_total": str(order.product_total),
                "total": str(order.total),
            }
            for order in order_query_set[
                offset : (kwargs["limit"] + offset) if "limit" in kwargs else None
            ]
        ]

    @classmethod
    def _get_product_item_data(cls, product_item):
        return {
            "id": product_item.id,
            "item_total": str(product_item.item_total),
            "name": product_item.name,
            "product": product_item.product_id,
            "price": str(product_item.price),
            "productshippingitem_set": [
                cls._get_product_shipping_item_data(product_shipping_item)
                for product_shipping_item in (
                    product_item.productshippingitem_set.order_by("id")
                )
            ],
            "quantity": product_item.quantity,
            "shipping_total": str(product_item.shipping_total),
            "subtotal": str(product_item.subtotal),
            "total": str(product_item.total),
        }

    @staticmethod
    def _get_product_shipping_item_data(product_shipping_item):
        return {
            "fixed_fee": str(product_shipping_item.fixed_fee),
            "id": product_shipping_item.id,
            "item_total": str(product_shipping_item.item_total),
            "name": product_shipping_item.name,
            "product_shipping": product_shipping_item.product_shipping_id,
            "subtotal": str(product_shipping_item.subtotal),
            "total": str(product_shipping_item.total),
            "unit_fee": str(product_shipping_item.unit_fee),
        }

    @staticmethod
    def _sorted_data_list_by_id(order_data_list):
        for order_data in order_data_list:
            order_data["productitem_set"] = sorted(
                order_data["productitem_set"],
                key=lambda product_item_data: product_item_data["id"],
            )
            for product_item_data in order_data["productitem_set"]:
                product_item_data["productshippingitem_set"] = sorted(
                    product_item_data["productshippingitem_set"],
                    key=lambda product_shipping_item_data: product_shipping_item_data[
                        "id"
                    ],
                )
        return order_data_list


class OrderViewSetTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 2, None, 2)
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {**data, "organization_id": self.organization.id}
        product_item_data_list = filter_.pop("productitem_set")
        order = Order.objects.filter(**filter_).first()
        self.assertIsNotNone(order)
        for product_item_data in product_item_data_list:
            filter_ = {**product_item_data, "order_id": order.id}
            product_shipping_item_data_list = filter_.pop("productshippingitem_set")
            product_item = ProductItem.objects.filter(**filter_).first()
            self.assertIsNotNone(product_item)
            for product_shipping_item_data in product_shipping_item_data_list:
                filter_ = {
                    **product_shipping_item_data,
                    "product_item_id": product_item.id,
                }
                product_shipping_item = ProductShippingItem.objects.filter(
                    **filter_
                ).first()
                self.assertIsNotNone(product_shipping_item)

    def test_create__code_already_in_another_order(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        order = OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["code"] = order.code
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"code": ["Code is already in another order."]}
        )

    def test_create__product_total_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["product_total"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"non_field_errors": ["Product total is incorrect."]}
        )

    def test_create__total_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["total"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"non_field_errors": ["Total is incorrect."]})

    def test_destroy(self):
        order = OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())
        self.assertFalse(ProductItem.objects.filter(order_id=order.id).exists())

    def test_list__filter__code__icontains(self):
        OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        for n in range(2):
            OrderWithRelatedFactory.create(
                {"code": f"-code-{n}"},
                self.organization,
                None,
                0,
                None,
                0,
            )
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"code__icontains": "code-"}
        response = self.client.get(path, data, format="json")
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__created_at__gte(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "created_at__gte": sorted(
                [
                    order.created_at
                    for order in [
                        OrderWithRelatedFactory.create(
                            {}, self.organization, None, 0, None, 0
                        )
                        for _ in range(3)
                    ]
                ]
            )[1]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__created_at__lte(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "created_at__lte": sorted(
                [
                    order.created_at
                    for order in [
                        OrderWithRelatedFactory.create(
                            {}, self.organization, None, 0, None, 0
                        )
                        for _ in range(3)
                    ]
                ]
            )[1]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__product_total__gte(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "product_total__gte": sorted(
                [
                    order.product_total
                    for order in [
                        OrderWithRelatedFactory.create(
                            {}, self.organization, None, 1, None, 1
                        )
                        for _ in range(3)
                    ]
                ]
            )[1]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__product_total__lte(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "product_total__lte": sorted(
                [
                    order.product_total
                    for order in [
                        OrderWithRelatedFactory.create(
                            {}, self.organization, None, 1, None, 1
                        )
                        for _ in range(3)
                    ]
                ]
            )[1]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__productitem__product__in(self):
        OrderWithRelatedFactory.create({}, self.organization, None, 1, None, 0)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "productitem__product__in": [
                order.productitem_set.all()[0].product.id
                for order in [
                    OrderWithRelatedFactory.create(
                        {}, self.organization, None, 1, None, 0
                    )
                    for _ in range(2)
                ]
            ]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__total__gte(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "total__gte": sorted(
                [
                    order.product_total
                    for order in [
                        OrderWithRelatedFactory.create(
                            {}, self.organization, None, 1, None, 1
                        )
                        for _ in range(3)
                    ]
                ]
            )[1]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__filter__total__lte(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {
            "total__lte": sorted(
                [
                    order.product_total
                    for order in [
                        OrderWithRelatedFactory.create(
                            {}, self.organization, None, 1, None, 1
                        )
                        for _ in range(3)
                    ]
                ]
            )[1]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__paginate(self):
        for _ in range(4):
            OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            self._sorted_data_list_by_id(response.json()["results"]),
            self._get_expected_data_list(data),
        )

    def test_list__sort__code(self):
        for _ in range(2):
            OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "code"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__sort__created_at(self):
        for _ in range(2):
            OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "created_at"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__sort__product_total(self):
        for _ in range(2):
            OrderWithRelatedFactory.create({}, self.organization, None, 1, None, 1)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "product_total"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_list__sort__total(self):
        for _ in range(2):
            OrderWithRelatedFactory.create({}, self.organization, None, 1, None, 1)
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = {"ordering": "total"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            self._sorted_data_list_by_id(response.json()),
            self._get_expected_data_list(data),
        )

    def test_partial_update(self):
        order = OrderWithRelatedFactory.create({}, self.organization, None, 2, None, 2)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 2, None, 2)
        product_item = order.product_items[0]
        data["productitem_set"][0]["id"] = product_item.id
        data["productitem_set"][0]["productshippingitem_set"][0][
            "id"
        ] = product_item.product_shipping_items[0].id
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = {**data, "organization_id": self.organization.id}
        product_item_data_list = filter_.pop("productitem_set")
        order = Order.objects.filter(**filter_).first()
        self.assertIsNotNone(order)
        for product_item_data in product_item_data_list:
            filter_ = {**product_item_data, "order_id": order.id}
            product_shipping_item_data_list = filter_.pop("productshippingitem_set")
            product_item = ProductItem.objects.filter(**filter_).first()
            self.assertIsNotNone(product_item)
            for product_shipping_item_data in product_shipping_item_data_list:
                filter_ = {
                    **product_shipping_item_data,
                    "product_item_id": product_item.id,
                }
                product_shipping_item = ProductShippingItem.objects.filter(
                    **filter_
                ).first()
                self.assertIsNotNone(product_shipping_item)

    def test_retrieve(self):
        order = OrderWithRelatedFactory.create({}, self.organization, None, 2, None, 2)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(
            self._sorted_data_list_by_id([response.json()]),
            self._get_expected_data_list({"id": order.id}),
        )


class ProductItemValidationTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create__item_total_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["productitem_set"][0]["item_total"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"productitem_set": [{"non_field_errors": ["Item total is incorrect."]}]},
        )

    def test_create__item_subtotal_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["productitem_set"][0]["subtotal"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"productitem_set": [{"non_field_errors": ["Subtotal is incorrect."]}]},
        )

    def test_create__product_in_another_organization(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data(
            {}, self.organization, ProductFactory.create(), 1, None, 0
        )
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {"product": ["Product is in another organization."]},
                ]
            },
        )

    def test_create__total_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["productitem_set"][0]["total"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"productitem_set": [{"non_field_errors": ["Total is incorrect."]}]},
        )

    def test_partial_update__product_item_not_belong_to_order(self):
        order = OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 0)
        data["productitem_set"][0]["id"] = 0
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"productitem_set": [{"id": ["Product item does not belong to order."]}]},
        )


class ProductShippingItemValidationTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create__item_total_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 1)
        data["productitem_set"][0]["productshippingitem_set"][0]["item_total"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {
                        "productshippingitem_set": [
                            {"non_field_errors": ["Item total is incorrect."]}
                        ]
                    }
                ]
            },
        )

    def test_create__item_subtotal_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 1)
        data["productitem_set"][0]["productshippingitem_set"][0]["subtotal"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {
                        "productshippingitem_set": [
                            {"non_field_errors": ["Subtotal is incorrect."]}
                        ]
                    }
                ]
            },
        )

    def test_create__product_item_in_another_organization(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data(
            {}, self.organization, None, 1, ProductShippingFactory.create(), 1
        )
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {
                        "productshippingitem_set": [
                            {
                                "product_shipping": [
                                    "Product shipping is in another organization."
                                ]
                            }
                        ]
                    },
                ]
            },
        )

    def test_create__total_incorrect(self):
        path = reverse("order-list", kwargs={"organization_id": self.organization.id})
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 1)
        data["productitem_set"][0]["productshippingitem_set"][0]["total"] += 1
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {
                        "productshippingitem_set": [
                            {"non_field_errors": ["Total is incorrect."]}
                        ]
                    }
                ]
            },
        )

    def test_partial_update__product_shipping_item_not_belong_to_order(self):
        order = OrderWithRelatedFactory.create({}, self.organization, None, 0, None, 0)
        path = reverse(
            "order-detail",
            kwargs={"organization_id": self.organization.id, "pk": order.id},
        )
        data = OrderWithRelatedFactory.get_data({}, self.organization, None, 1, None, 1)
        data["productitem_set"][0]["productshippingitem_set"][0]["id"] = 0
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "productitem_set": [
                    {
                        "productshippingitem_set": [
                            {
                                "id": [
                                    "Product shipping item does not belong to product"
                                    " item."
                                ]
                            }
                        ]
                    }
                ]
            },
        )
