from random import shuffle

from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.product_factory import ProductFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.models import ZONE_CHOICES
from main.models.product import Product
from main.models.product_shipping import ProductShipping
from main.test_cases.staff_test_case import StaffTestCase
from main.tests import faker


class ProductShippingViewSetTestCase(StaffTestCase):
    def test_create(self):
        built_product_shipping = ProductShippingFactory.build()
        products = ProductFactory.create_batch(2, organization=self.organization)
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "code": built_product_shipping.code,
            "fixed_fee": built_product_shipping.fixed_fee,
            "name": built_product_shipping.name,
            "products": tuple(product.id for product in products),
            "unit_fee": built_product_shipping.unit_fee,
            "zones": built_product_shipping.zones,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        product_ids = data.pop("products")
        filter_ = {**data, "organization_id": self.organization.id}
        product_shipping = ProductShipping.objects.filter(**filter_).first()
        self.assertIsNotNone(product_shipping)
        self.assertCountEqual(
            Product.objects.filter(productshipping=product_shipping.id).values_list(
                "id", flat=True
            ),
            product_ids,
        )

    def test_create__code_already_in_another_product_shipping(self):
        product_shipping = ProductShippingFactory.create(organization=self.organization)
        built_product_shipping = ProductShippingFactory.build(
            organization=self.organization
        )
        products = ProductFactory.create_batch(2, organization=self.organization)
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "code": product_shipping.code,
            "fixed_fee": built_product_shipping.fixed_fee,
            "name": built_product_shipping.name,
            "products": tuple(product.id for product in products),
            "unit_fee": built_product_shipping.unit_fee,
            "zones": built_product_shipping.zones,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"code": ["Code is already in another product shipping."]}
        )

    def test_create__products_already_have_shipping_with_zones(self):
        zones = faker.random_choices(
            elements=tuple(choice[0] for choice in ZONE_CHOICES), length=3
        )
        product_shipping = ProductShippingFactory.create(
            organization=self.organization, zones=zones[0:2]
        )
        built_product_shipping = ProductShippingFactory.build(
            organization=self.organization
        )
        products = ProductFactory.create_batch(3, organization=self.organization)
        product_shipping.products.set(products[0:2])
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "code": built_product_shipping.code,
            "fixed_fee": built_product_shipping.fixed_fee,
            "name": built_product_shipping.name,
            "products": tuple(product.id for product in products[1:3]),
            "unit_fee": built_product_shipping.unit_fee,
            "zones": zones[1:3],
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"non_field_errors": ["Products already have shipping with zones."]},
        )

    def test_create__products_in_another_organizations(self):
        built_product_shipping = ProductShippingFactory.build(
            organization=self.organization
        )
        products = ProductFactory.create_batch(2)
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "code": built_product_shipping.code,
            "fixed_fee": built_product_shipping.fixed_fee,
            "name": built_product_shipping.name,
            "products": tuple(product.id for product in products),
            "unit_fee": built_product_shipping.unit_fee,
            "zones": built_product_shipping.zones,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"products": ["Products are in another organization."]}
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

    def test_list__filter__fixed_fee__gte(self):
        fixed_fee = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=4)
            for _ in range(3)
        ]
        fixed_fee.sort(reverse=True)
        ProductShippingFactory.create(
            organization=self.organization, fixed_fee=fixed_fee.pop()
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization=self.organization,
            fixed_fee=Iterator(fixed_fee),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fixed_fee__gte": product_shipping_list[-1].fixed_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__fixed_fee__lte(self):
        fixed_fee = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=4)
            for _ in range(3)
        ]
        fixed_fee.sort()
        ProductShippingFactory.create(
            organization=self.organization, fixed_fee=fixed_fee.pop()
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization=self.organization,
            fixed_fee=Iterator(fixed_fee),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fixed_fee__lte": product_shipping_list[-1].fixed_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__unit_fee__gte(self):
        unit_fee = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=4)
            for _ in range(3)
        ]
        unit_fee.sort(reverse=True)
        ProductShippingFactory.create(
            organization=self.organization, unit_fee=unit_fee.pop()
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization=self.organization,
            unit_fee=Iterator(unit_fee),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"unit_fee__gte": product_shipping_list[-1].unit_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), product_shipping_list)

    def test_list__filter__unit_fee__lte(self):
        unit_fee = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=4)
            for _ in range(3)
        ]
        unit_fee.sort()
        ProductShippingFactory.create(
            organization=self.organization, unit_fee=unit_fee.pop()
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2,
            organization=self.organization,
            unit_fee=Iterator(unit_fee),
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"unit_fee__lte": product_shipping_list[-1].unit_fee}
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

    def test_list__filter__products__id__in(self):
        ProductShippingFactory.create(organization=self.organization)
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization
        )
        product_dict = {}
        for product_shipping in product_shipping_list:
            products = ProductFactory.create_batch(2, organization=self.organization)
            product_shipping.products.set(products)
            product_dict[product_shipping.id] = products
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "products__in": tuple(
                product.id
                for product_shipping_id in product_dict
                for product in product_dict[product_shipping_id]
            )
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json(), product_shipping_list, product_dict=product_dict
        )

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
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.id)
        paginated_product_shipping_list = (
            product_shipping_list[1],
            product_shipping_list[2],
        )
        product_dict = {}
        for product_shipping in paginated_product_shipping_list:
            products = ProductFactory.create_batch(2, organization=self.organization)
            product_shipping.products.set(products)
            product_dict[product_shipping.id] = products
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            response.json()["results"],
            paginated_product_shipping_list,
            is_ordered=True,
            product_dict=product_dict,
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

    def test_list__sort__fixed_fee(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "fixed_fee"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.fixed_fee
        )
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

    def test_list__sort__unit_fee(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "unit_fee"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee
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
        products = ProductFactory.create_batch(3, organization=self.organization)
        product_shipping.products.set(products[0:2])
        path = reverse(
            "productshipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": product_shipping.id},
        )
        data = {
            "code": built_product_shipping.code,
            "fixed_fee": built_product_shipping.fixed_fee,
            "name": built_product_shipping.name,
            "products": tuple(product.id for product in products[1:3]),
            "unit_fee": built_product_shipping.unit_fee,
            "zones": zones[1:3],
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        product_ids = data.pop("products")
        filter_ = {
            **data,
            "id": product_shipping.id,
            "organization_id": self.organization.id,
        }
        product_shipping = ProductShipping.objects.filter(**filter_).first()
        self.assertIsNotNone(product_shipping)
        self.assertCountEqual(
            Product.objects.filter(productshipping=product_shipping.id).values_list(
                "id", flat=True
            ),
            product_ids,
        )

    def test_retrieve(self):
        product_shipping = ProductShippingFactory.create(organization=self.organization)
        products = ProductFactory.create_batch(2, organization=self.organization)
        product_shipping.products.set(products)
        path = reverse(
            "productshipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": product_shipping.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            (response.json(),),
            (product_shipping,),
            products,
        )

    def _assertGetResponseData(
        self, actual1, product_shipping_list, is_ordered=False, product_dict=None
    ):
        actual2 = {dict_["id"]: dict_.pop("products") for dict_ in actual1}
        expected = [
            {
                "code": product_shipping.code,
                "fixed_fee": str(product_shipping.fixed_fee),
                "id": product_shipping.id,
                "name": product_shipping.name,
                "unit_fee": str(product_shipping.unit_fee),
                "zones": product_shipping.zones,
            }
            for product_shipping in product_shipping_list
        ]
        if is_ordered:
            self.assertSequenceEqual(actual1, expected)
        else:
            self.assertCountEqual(actual1, expected)
        if product_dict is not None:
            self.assertCountEqual(
                tuple(id_ for id_ in actual2), tuple(id_ for id_ in product_dict)
            )
            for id_, product_ids in actual2.items():
                self.assertCountEqual(
                    product_ids, (product.id for product in product_dict[id_])
                )
