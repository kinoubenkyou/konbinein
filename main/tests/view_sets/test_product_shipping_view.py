from random import shuffle

from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.product_shipping_factory import ProductShippingFactory
from main.models import ZONE_CHOICES
from main.models.product_shipping import ProductShipping
from main.test_cases.staff_test_case import StaffTestCase
from main.tests import faker


class ProductShippingViewSetTestCase(StaffTestCase):
    def test_create(self):
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        built_product_shipping = ProductShippingFactory.build()
        data = {
            "code": built_product_shipping.code,
            "fee": built_product_shipping.fee,
            "name": built_product_shipping.name,
            "shipping_type": built_product_shipping.shipping_type,
            "zones": built_product_shipping.zones,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = data | {"organization_id": self.organization.id}
        product_shipping = ProductShipping.objects.filter(**filter_).first()
        self.assertIsNotNone(product_shipping)

    def test_create__code_already_in_another_product_shipping(self):
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        product_shipping = ProductShippingFactory.create(organization=self.organization)
        built_product_shipping = ProductShippingFactory.build(
            organization=self.organization
        )
        data = {
            "code": product_shipping.code,
            "fee": built_product_shipping.fee,
            "name": built_product_shipping.name,
            "shipping_type": built_product_shipping.shipping_type,
            "zones": built_product_shipping.zones,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"code": ["Code is already in another product shipping."]}
        )

    def test_create__zones_already_in_another_product_shipping(self):
        zones = faker.random_choices(
            elements=tuple(choice[0] for choice in ZONE_CHOICES), length=3
        )
        ProductShippingFactory.create(organization=self.organization, zones=zones[0:2])
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        built_product_shipping = ProductShippingFactory.build(
            organization=self.organization
        )
        data = {
            "code": built_product_shipping.code,
            "fee": built_product_shipping.fee,
            "name": built_product_shipping.name,
            "shipping_type": built_product_shipping.shipping_type,
            "zones": zones[1:3],
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"zones": ["Zones are already in another product shipping."]},
        )

    def test_destroy(self):
        product_shipping = ProductShippingFactory.create(organization=self.organization)
        path = reverse(
            "productshipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": product_shipping.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(
            ProductShipping.objects.filter(id=product_shipping.id).exists()
        )

    def test_list__filter__code__in(self):
        ProductShippingFactory.create(organization=self.organization)
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "code__in": tuple(
                product_shipping.code for product_shipping in product_shipping_list
            )
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__fee__gte(self):
        fees = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=2)
            for _ in range(3)
        ]
        fees.sort(reverse=True)
        ProductShippingFactory.create(organization=self.organization, fee=fees.pop())
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization=self.organization,
            fee=Iterator(fees),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fee__gte": product_shipping_list[-1].fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__fee__lte(self):
        fees = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=2)
            for _ in range(3)
        ]
        fees.sort()
        ProductShippingFactory.create(organization=self.organization, fee=fees.pop())
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization=self.organization,
            fee=Iterator(fees),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fee__lte": product_shipping_list[-1].fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__name__in(self):
        ProductShippingFactory.create(organization=self.organization)
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "name__in": tuple(
                product_shipping.name for product_shipping in product_shipping_list
            )
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__shipping_type__in(self):
        shipping_types = [choice[0] for choice in ProductShipping.SHIPPING_TYPE_CHOICES]
        shuffle(shipping_types)
        ProductShippingFactory.create(
            organization=self.organization, shipping_type=shipping_types[0]
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization, shipping_type=shipping_types[1]
        )
        data = {
            "shipping_type__in": tuple(
                product_shipping.shipping_type
                for product_shipping in product_shipping_list
            )
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__zones__overlap(self):
        zones = [choice[0] for choice in ZONE_CHOICES]
        shuffle(zones)
        ProductShippingFactory.create(organization=self.organization, zones=zones[0:2])
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization, zones=Iterator((zones[2:4], zones[4:6]))
        )
        data = {"zones__overlap": zones[3:5]}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__paginate(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            4, organization=self.organization
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.id)
        self._assertGetResponseData(
            response.json()["results"],
            (product_shipping_list[1], product_shipping_list[2]),
            is_ordered=True,
        )

    def test_list__sort__code(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.code)
        self._assertGetResponseData(
            response.json(), product_shipping_list, is_ordered=True
        )

    def test_list__sort__fee(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "fee"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.fee)
        self._assertGetResponseData(
            response.json(), product_shipping_list, is_ordered=True
        )

    def test_list__sort__name(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "name"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.name)
        self._assertGetResponseData(
            response.json(), product_shipping_list, is_ordered=True
        )

    def test_list__sort__shipping_type(self):
        shipping_types = [choice[0] for choice in ProductShipping.SHIPPING_TYPE_CHOICES]
        shuffle(shipping_types)
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization_id=self.organization.id,
            shipping_type=Iterator(shipping_types),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(
            path, data={"ordering": "shipping_type"}, format="json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.shipping_type
        )
        self._assertGetResponseData(
            response.json(), product_shipping_list, is_ordered=True
        )

    def test_partial_update(self):
        zones = faker.random_choices(
            elements=tuple(choice[0] for choice in ZONE_CHOICES), length=3
        )
        product_shipping = ProductShippingFactory.create(
            organization=self.organization, zones=zones[0:2]
        )
        built_product_shipping = ProductShippingFactory.build()
        path = reverse(
            "productshipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": product_shipping.id},
        )
        data = {
            "code": built_product_shipping.code,
            "fee": built_product_shipping.fee,
            "name": built_product_shipping.name,
            "shipping_type": built_product_shipping.shipping_type,
            "zones": zones[1:3],
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = data | {
            "id": product_shipping.id,
            "organization_id": self.organization.id,
        }
        self.assertTrue(ProductShipping.objects.filter(**filter_).exists())

    def test_retrieve(self):
        product_shipping = ProductShippingFactory.create(organization=self.organization)
        path = reverse(
            "productshipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": product_shipping.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            (response.json(),),
            (product_shipping,),
        )

    def _assertGetResponseData(self, actual, product_shipping_list, is_ordered=False):
        expected = [
            {
                "code": product_shipping.code,
                "fee": f"{product_shipping.fee:.4f}",
                "name": product_shipping.name,
                "shipping_type": product_shipping.shipping_type,
                "zones": product_shipping.zones,
            }
            for product_shipping in product_shipping_list
        ]
        if is_ordered:
            self.assertEqual(actual, expected)
        else:
            self.assertCountEqual(actual, expected)
