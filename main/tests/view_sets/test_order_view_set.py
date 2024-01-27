from main.factories.order_with_related_factory import OrderWithRelatedFactory
from main.factories.product_factory import ProductFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.models.order import Order
from main.models.product_item import ProductItem
from main.models.product_shipping_item import ProductShippingItem
from main.tests.staff_test_case import StaffTestCase
from main.tests.view_sets.organization_view_set_test_case_mixin import (
    OrganizationViewSetTestCaseMixin,
)


class OrderViewSetTestCaseMixin(OrganizationViewSetTestCaseMixin):
    basename = "order"
    model = Order

    def _assert_destroyed_order(self, order):
        self.assertIsNone(Order.objects.filter(id=order.id).first())
        self._assert_destroyed_product_item(order.cached_product_items)

    def _assert_destroyed_product_item(self, product_items):
        self.assertIsNone(
            ProductItem.objects.filter(
                id__in=[product_item.id for product_item in product_items]
            ).first()
        )
        self._assert_destroyed_product_shipping_item([
            product_shipping_item
            for product_item in product_items
            for product_shipping_item in product_item.cached_product_shipping_items
        ])

    def _assert_destroyed_product_shipping_item(self, product_shipping_items):
        self.assertIsNone(
            ProductShippingItem.objects.filter(
                id__in=[
                    product_shipping_item.id
                    for product_shipping_item in product_shipping_items
                ]
            ).first()
        )

    def _assert_saved_object(self, filter_):
        product_item_filters = filter_.pop("productitem_set")
        order = Order.objects.filter(**filter_).first()
        self.assertIsNotNone(order)
        for product_item_filter in product_item_filters:
            product_item_filter["order_id"] = order.id
            self._assert_saved_product_item(product_item_filter)

    def _assert_saved_product_item(self, product_item_filter):
        product_item_shipping_filters = product_item_filter.pop(
            "productshippingitem_set"
        )
        product_item = ProductItem.objects.filter(**product_item_filter).first()
        self.assertIsNotNone(product_item)
        for product_item_shipping_filter in product_item_shipping_filters:
            product_item_shipping_filter["product_item_id"] = product_item.id
            self._assert_saved_product_shipping_item(product_item_shipping_filter)

    def _assert_saved_product_shipping_item(self, product_item_shipping_filter):
        self.assertIsNotNone(
            ProductShippingItem.objects.filter(**product_item_shipping_filter).first()
        )

    @classmethod
    def _serializer_data(cls, order):
        product_item_data_list = [
            cls._product_item_data(product_item)
            for product_item in order.productitem_set.order_by("id")
        ]
        product_item_data_list.sort(
            key=lambda product_item_data: product_item_data["id"]
        )
        return {
            "code": order.code,
            "created_at": order.created_at.isoformat(),
            "id": order.id,
            "product_shipping_total": str(order.product_shipping_total),
            "product_total": str(order.product_total),
            "productitem_set": product_item_data_list,
            "total": str(order.total),
        }

    @classmethod
    def _product_item_data(cls, product_item):
        product_shipping_item_data_list = [
            cls._product_shipping_item_data(product_shipping_item)
            for product_shipping_item in (
                product_item.productshippingitem_set.order_by("id")
            )
        ]
        product_shipping_item_data_list.sort(
            key=lambda product_shipping_item_data: product_shipping_item_data["id"]
        )
        return {
            "id": product_item.id,
            "item_total": str(product_item.item_total),
            "name": product_item.name,
            "product": product_item.product_id,
            "price": str(product_item.price),
            "productshippingitem_set": product_shipping_item_data_list,
            "quantity": product_item.quantity,
        }

    @staticmethod
    def _product_shipping_item_data(product_shipping_item):
        return {
            "fixed_fee": str(product_shipping_item.fixed_fee),
            "id": product_shipping_item.id,
            "item_total": str(product_shipping_item.item_total),
            "name": product_shipping_item.name,
            "product_shipping": product_shipping_item.product_shipping_id,
            "unit_fee": str(product_shipping_item.unit_fee),
        }


class OrderValidationTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create__code_already_in_another_order(self):
        order = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create()
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["code"] = order.code
        self._act_and_assert_create_validation_test(
            data, {"code": ["Code is already in another order."]}
        )

    def test_create__product_total_incorrect(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["product_total"] += 1
        self._act_and_assert_create_validation_test(
            data, {"non_field_errors": ["Product total is incorrect."]}
        )

    def test_create__product_shipping_total_incorrect(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=1,
            product_shipping_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["product_shipping_total"] += 1
        self._act_and_assert_create_validation_test(
            data, {"non_field_errors": ["Product shipping total is incorrect."]}
        )

    def test_create__total_incorrect(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=1,
            product_shipping_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["total"] += 1
        self._act_and_assert_create_validation_test(
            data, {"non_field_errors": ["Total is incorrect."]}
        )


class OrderViewSetTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        filter_ = {**data, "organization_id": self.organization.id}
        self._act_and_assert_create_test(data, filter_)

    def test_destroy(self):
        order = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create()
        self._act_and_assert_destroy_test_response_status(order.id)
        self._assert_destroyed_order(order)

    def test_list__filter__code__icontains(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create()
        for n in range(2):
            OrderWithRelatedFactory(
                order_kwargs={"code": f"-code--{n}", "organization": self.organization},
            ).create()
        self._act_and_assert_list_test({"code__icontains": "code--"})

    def test_list__filter__created_at__gte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.created_at, reverse=True)
        self._act_and_assert_list_test({"created_at__gte": orders[1].created_at})

    def test_list__filter__created_at__lte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.created_at)
        self._act_and_assert_list_test({"created_at__lte": orders[1].created_at})

    def test_list__filter__product_shipping_total__gte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.product_total, reverse=True)
        self._act_and_assert_list_test({
            "product_shipping_total__gte": orders[1].product_shipping_total
        })

    def test_list__filter__product_shipping_total__lte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.product_total)
        self._act_and_assert_list_test({
            "product_shipping_total__lte": orders[1].product_shipping_total
        })

    def test_list__filter__productitem__productshippingitem__product_shipping__in(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create()
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({
            "productitem__productshippingitem__product_shipping__in": [
                product_shipping_item.product_shipping.id
                for order in orders
                for product_item in order.productitem_set.all()
                for product_shipping_item in product_item.productshippingitem_set.all()
            ]
        })

    def test_list__filter__product_total__gte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.product_total, reverse=True)
        self._act_and_assert_list_test({"product_total__gte": orders[1].product_total})

    def test_list__filter__product_total__lte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.product_total)
        self._act_and_assert_list_test({"product_total__lte": orders[1].product_total})

    def test_list__filter__productitem__product__in(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
        ).create()
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({
            "productitem__product__in": [
                product_item.product.id
                for order in orders
                for product_item in order.productitem_set.all()
            ]
        })

    def test_list__filter__total__gte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.total, reverse=True)
        self._act_and_assert_list_test({"total__gte": orders[1].total})

    def test_list__filter__total__lte(self):
        orders = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(3)
        orders.sort(key=lambda order: order.total)
        self._act_and_assert_list_test({"total__lte": orders[1].total})

    def test_list__paginate(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create_batch(4)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__code(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "code"})

    def test_list__sort__created_at(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "created_at"})

    def test_list__sort__product_shipping_total(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "product_shipping_total"})

    def test_list__sort__product_total(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "product_total"})

    def test_list__sort__total(self):
        OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "total"})

    def test_partial_update(self):
        order = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).create()
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=2,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=2,
            product_shipping_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        product_item = order.cached_product_items[0]
        data["productitem_set"][0]["id"] = product_item.id
        data["productitem_set"][0]["productshippingitem_set"][0]["id"] = (
            product_item.cached_product_shipping_items[0].id
        )
        filter_ = {**data, "organization_id": self.organization.id}
        self._act_and_assert_partial_update_test(data, filter_, order.id)

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(
            OrderWithRelatedFactory(
                order_kwargs={"organization": self.organization},
                product_item_count=2,
                product_kwargs={"organization": self.organization},
                product_shipping_item_count=2,
                product_shipping_kwargs={"organization": self.organization},
            )
            .create()
            .id
        )


class ProductItemValidationTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create__item_total_incorrect(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["productitem_set"][0]["item_total"] += 1
        self._act_and_assert_create_validation_test(
            data,
            {"productitem_set": [{"non_field_errors": ["Item total is incorrect."]}]},
        )

    def test_create__product_in_another_organization(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product=ProductFactory.create(),
            product_item_count=1,
            product_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        self._act_and_assert_create_validation_test(
            data,
            {
                "productitem_set": [
                    {"product": ["Product is in another organization."]},
                ]
            },
        )

    def test_partial_update__product_item_not_belong_to_order(self):
        order = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create()
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["productitem_set"][0]["id"] = 0
        self._act_and_assert_partial_update_validation_test(
            data,
            {"productitem_set": [{"id": ["Product item can't be found."]}]},
            order.id,
        )


class ProductShippingItemValidationTestCase(OrderViewSetTestCaseMixin, StaffTestCase):
    def test_create__item_total_incorrect(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=1,
            product_shipping_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["productitem_set"][0]["productshippingitem_set"][0]["item_total"] += 1
        self._act_and_assert_create_validation_test(
            data,
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

    def test_create__product_item_in_another_organization(self):
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
            product_shipping=ProductShippingFactory.create(),
            product_shipping_item_count=1,
        ).get_deserializer_data()
        self._act_and_assert_create_validation_test(
            data,
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

    def test_partial_update__product_shipping_item_not_belong_to_order(self):
        order = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
        ).create()
        data = OrderWithRelatedFactory(
            order_kwargs={"organization": self.organization},
            product_item_count=1,
            product_kwargs={"organization": self.organization},
            product_shipping_item_count=1,
            product_shipping_kwargs={"organization": self.organization},
        ).get_deserializer_data()
        data["productitem_set"][0]["productshippingitem_set"][0]["id"] = 0
        self._act_and_assert_partial_update_validation_test(
            data,
            {
                "productitem_set": [
                    {
                        "productshippingitem_set": [
                            {"id": ["Product shipping item can't be found."]}
                        ]
                    }
                ]
            },
            order.id,
        )
