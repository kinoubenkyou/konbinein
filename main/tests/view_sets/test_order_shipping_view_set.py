from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.order_shipping_factory import OrderShippingFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.models import ZONE_CHOICES
from main.models.order_shipping import OrderShipping
from main.tests import faker
from main.tests.staff_test_case import StaffTestCase


class OrderShippingViewSetTestCase(StaffTestCase):
    def test_create(self):
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = self._create_data()
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {**data, "organization_id": self.organization.id}
        order_shipping = OrderShipping.objects.filter(**filter_).first()
        self.assertIsNotNone(order_shipping)

    def test_create__code_already_in_another_product_shipping(self):
        order_shipping = OrderShippingFactory.create(organization=self.organization)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = self._create_data()
        data["code"] = order_shipping.code
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"code": ["Code is already in another order shipping."]}
        )

    def test_destroy(self):
        order_shipping = OrderShippingFactory.create(organization=self.organization)
        path = reverse(
            "ordershipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": order_shipping.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(OrderShipping.objects.filter(id=order_shipping.id).exists())

    def test_list__filter__code__icontains(self):
        OrderShippingFactory.create(organization=self.organization)
        ProductShippingFactory.create_batch(
            2,
            code=Iterator(range(2), getter=lambda n: f"-code-{n}"),
            organization=self.organization,
        )
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"code__icontains": "code-"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__filter__fixed_fee__gte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(
            key=lambda order_shipping: order_shipping.fixed_fee, reverse=True
        )
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fixed_fee__gte": order_shipping_list[1].fixed_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__filter__fixed_fee__lte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.fixed_fee)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fixed_fee__lte": order_shipping_list[1].fixed_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__filter__name__icontains(self):
        OrderShippingFactory.create(organization=self.organization)
        OrderShippingFactory.create_batch(
            2,
            name=Iterator(range(2), getter=lambda n: f"-name-{n}"),
            organization=self.organization,
        )
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"name__icontains": "name-"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__filter__unit_fee__gte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee, reverse=True
        )
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"unit_fee__gte": order_shipping_list[1].unit_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__filter__unit_fee__lte(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            3, organization=self.organization
        )
        order_shipping_list.sort(key=lambda product_shipping: product_shipping.unit_fee)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"unit_fee__gte": order_shipping_list[1].unit_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__filter__zones__overlap(self):
        zones = [choice[0] for choice in ZONE_CHOICES]
        OrderShippingFactory.create(
            organization=self.organization, zones=[zones.pop(), zones.pop()]
        )
        order_shipping_list = OrderShippingFactory.create_batch(
            2, organization=self.organization, zones=[zones.pop(), zones.pop()]
        )
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "zones__overlap": [
                order_shipping.zones[0] for order_shipping in order_shipping_list
            ]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__paginate(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            4, organization=self.organization
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.id)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json()["results"], self._expected_data_list(data)
        )

    def test_list__sort__code(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.code)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "code"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__sort__fixed_fee(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.fixed_fee)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "fixed_fee"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__sort__name(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.name)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "name"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_list__sort__unit_fee(self):
        order_shipping_list = OrderShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        order_shipping_list.sort(key=lambda order_shipping: order_shipping.unit_fee)
        path = reverse(
            "ordershipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"ordering": "unit_fee"}
        response = self.client.get(path, data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list(data))

    def test_partial_update(self):
        zones = faker.random_choices(
            elements=[choice[0] for choice in ZONE_CHOICES], length=3
        )
        order_shipping = OrderShippingFactory.create(
            organization=self.organization, zones=zones[0:2]
        )
        path = reverse(
            "ordershipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": order_shipping.id},
        )
        data = self._create_data()
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = {
            **data,
            "id": order_shipping.id,
            "organization_id": self.organization.id,
        }
        order_shipping = OrderShipping.objects.filter(**filter_).first()
        self.assertIsNotNone(order_shipping)

    def test_retrieve(self):
        order_shipping = OrderShippingFactory.create(organization=self.organization)
        path = reverse(
            "ordershipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": order_shipping.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            [response.json()], self._expected_data_list({"id": order_shipping.id})
        )

    @staticmethod
    def _create_data():
        order_shipping = OrderShippingFactory.build()
        return {
            "code": order_shipping.code,
            "fixed_fee": order_shipping.fixed_fee,
            "name": order_shipping.name,
            "unit_fee": order_shipping.unit_fee,
            "zones": order_shipping.zones,
        }

    @staticmethod
    def _expected_data_list(kwargs):
        filter_ = {
            key: value
            for key, value in kwargs.items()
            if key not in ["limit", "offset", "ordering"]
        }
        order_shipping_query_set = OrderShipping.objects.filter(**filter_)
        if "ordering" in kwargs:
            order_shipping_query_set = order_shipping_query_set.order_by(
                kwargs["ordering"]
            )
        offset = kwargs.get("offset", 0)
        return [
            {
                "code": order_shipping.code,
                "fixed_fee": str(order_shipping.fixed_fee),
                "id": order_shipping.id,
                "name": order_shipping.name,
                "unit_fee": str(order_shipping.unit_fee),
                "zones": order_shipping.zones,
            }
            for order_shipping in order_shipping_query_set[
                offset : (kwargs["limit"] + offset) if "limit" in kwargs else None
            ]
        ]
