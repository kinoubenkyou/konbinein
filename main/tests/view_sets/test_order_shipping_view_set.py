from random import sample

from factory import Iterator

from main.factories.order_shipping_factory import OrderShippingFactory
from main.models import ZONE_CHOICES
from main.models.order_shipping import OrderShipping
from main.tests.view_sets.organization_test_case import OrganizationTestCase
from main.view_sets.order_shipping_view_set import OrderShippingViewSet


class OrderShippingViewSetTestCase(OrganizationTestCase):
    basename = "ordershipping"
    view_set = OrderShippingViewSet

    def test_create(self):
        data = self._get_deserializer_data()
        self._act_and_assert_create_test(data, {**data})

    def test_create__code_already_in_another_product_shipping(self):
        order_shipping = OrderShippingFactory.create(organization=self.organization)
        data = {**self._get_deserializer_data(), "code": order_shipping.code}
        self._act_and_assert_create_validation_test(
            data, {"code": ["Code is already in another order shipping."]}
        )

    def test_destroy(self):
        self._act_and_assert_destroy_test(
            OrderShippingFactory.create(organization=self.organization)
        )

    def test_list__filter__code__icontains(self):
        OrderShippingFactory.create(organization=self.organization)
        OrderShippingFactory.create_batch(
            2,
            code=Iterator(range(2), getter=lambda n: f"-code--{n}"),
            organization=self.organization,
        )
        self._act_and_assert_list_test({"code__icontains": "code--"})

    def test_list__filter__fixed_fee__gte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(
            key=lambda order_shipping: order_shipping.fixed_fee, reverse=True
        )
        self._act_and_assert_list_test({
            "fixed_fee__gte": order_shipping_list[1].fixed_fee
        })

    def test_list__filter__fixed_fee__lte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.fixed_fee)
        self._act_and_assert_list_test({
            "fixed_fee__lte": order_shipping_list[1].fixed_fee
        })

    def test_list__filter__name__icontains(self):
        OrderShippingFactory.create(organization=self.organization)
        OrderShippingFactory.create_batch(
            2,
            name=Iterator(range(2), getter=lambda n: f"-name--{n}"),
            organization=self.organization,
        )
        self._act_and_assert_list_test({"name__icontains": "name--"})

    def test_list__filter__unit_fee__gte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee, reverse=True
        )
        self._act_and_assert_list_test({
            "unit_fee__gte": order_shipping_list[1].unit_fee
        })

    def test_list__filter__unit_fee__lte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(key=lambda product_shipping: product_shipping.unit_fee)
        self._act_and_assert_list_test({
            "unit_fee__lte": order_shipping_list[1].unit_fee
        })

    def test_list__filter__zones__overlap(self):
        zones = sample([choice[0] for choice in ZONE_CHOICES], 6)
        OrderShippingFactory.create(organization=self.organization, zones=zones[0:2])
        order_shipping_list = OrderShippingFactory.create_batch(
            2,
            organization=self.organization,
            zones=Iterator([zones[2:4], zones[4:6]]),
        )
        self._act_and_assert_list_test({
            "zones__overlap": [
                order_shipping.zones[0] for order_shipping in order_shipping_list
            ]
        })

    def test_list__paginate(self):
        OrderShippingFactory.create_batch(4, organization=self.organization)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__code(self):
        OrderShippingFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "code"})

    def test_list__sort__fixed_fee(self):
        OrderShippingFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "fixed_fee"})

    def test_list__sort__name(self):
        OrderShippingFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "name"})

    def test_list__sort__unit_fee(self):
        OrderShippingFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "unit_fee"})

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(
            OrderShippingFactory.create(organization=self.organization).id
        )

    def test_update(self):
        zones = sample([choice[0] for choice in ZONE_CHOICES], 3)
        order_shipping = OrderShippingFactory.create(
            organization=self.organization,
            zones=zones[1:3],
        )
        data = {**self._get_deserializer_data(), "zones": zones[0:2]}
        filter_ = {
            **data,
            "organization_id": self.organization.id,
        }
        self._act_and_assert_update_test(
            data,
            filter_,
            order_shipping.id,
        )

    @staticmethod
    def _get_deserializer_data():
        order_shipping = OrderShippingFactory.build()
        return {
            "code": order_shipping.code,
            "fixed_fee": str(order_shipping.fixed_fee),
            "name": order_shipping.name,
            "unit_fee": str(order_shipping.unit_fee),
            "zones": order_shipping.zones,
        }

    def _get_query_set(self):
        return OrderShipping.objects.filter(organization=self.organization.id)

    @staticmethod
    def _get_serializer_data(order_shipping):
        return {
            "code": order_shipping.code,
            "fixed_fee": str(order_shipping.fixed_fee),
            "id": order_shipping.id,
            "name": order_shipping.name,
            "unit_fee": str(order_shipping.unit_fee),
            "zones": order_shipping.zones,
        }
