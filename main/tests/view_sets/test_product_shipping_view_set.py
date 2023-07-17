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
from main.tests import faker
from main.tests.staff_test_case import StaffTestCase


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
            "products": [product.id for product in products],
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
            "products": [product.id for product in products],
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
            elements=[choice[0] for choice in ZONE_CHOICES], length=3
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
            "products": [product.id for product in products[1:3]],
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
            "products": [product.id for product in products],
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

    def test_list__filter__code__icontains(self):
        ProductShippingFactory.create(organization=self.organization)
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in ProductShippingFactory.create_batch(
                2,
                code=Iterator(range(2), getter=lambda n: f"-code-{n}"),
                organization=self.organization,
            )
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"code__icontains": "code-"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__fixed_fee__gte(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            3, organization=self.organization
        )
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.fixed_fee, reverse=True
        )
        product_shipping_list.pop()
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fixed_fee__gte": product_shipping_list[-1].fixed_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__fixed_fee__lte(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            3, organization=self.organization
        )
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.fixed_fee
        )
        product_shipping_list.pop()
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"fixed_fee__lte": product_shipping_list[-1].fixed_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__name__icontains(self):
        ProductShippingFactory.create(organization=self.organization)
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in ProductShippingFactory.create_batch(
                2,
                name=Iterator(range(2), getter=lambda n: f"-name-{n}"),
                organization=self.organization,
            )
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"name__icontains": "name-"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__unit_fee__gte(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            3, organization=self.organization
        )
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee, reverse=True
        )
        product_shipping_list.pop()
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"unit_fee__gte": product_shipping_list[-1].unit_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__unit_fee__lte(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            3, organization=self.organization
        )
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee
        )
        product_shipping_list.pop()
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"unit_fee__lte": product_shipping_list[-1].unit_fee}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__products__id__in(self):
        product_shipping = ProductShippingFactory.create(organization=self.organization)
        products = ProductFactory.create_batch(2, organization=self.organization)
        product_shipping.products.set(products)
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization
        )
        product_shipping_dicts = [
            {
                "object": product_shipping,
                "product_dicts": [
                    {"object": product}
                    for product in self._create_and_set_products(product_shipping)
                ],
            }
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "products__in": [
                product_dict["object"].id
                for product_shipping_dict in product_shipping_dicts
                for product_dict in product_shipping_dict["product_dicts"]
            ]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__filter__zones__overlap(self):
        zones = [choice[0] for choice in ZONE_CHOICES]
        ProductShippingFactory.create(
            organization=self.organization, zones=[zones.pop(), zones.pop()]
        )
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization=self.organization, zones=[zones.pop(), zones.pop()]
        )
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {
            "zones__overlap": [
                product_shipping_dict["object"].zones[0]
                for product_shipping_dict in product_shipping_dicts
            ]
        }
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, False)

    def test_list__paginate(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            4, organization=self.organization
        )
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.id)
        product_shipping_dicts = [
            {
                "object": product_shipping,
                "product_dicts": [
                    {"object": product}
                    for product in self._create_and_set_products(product_shipping)
                ],
            }
            for product_shipping in product_shipping_list[1:3]
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(
            response.json()["results"], product_shipping_dicts, False
        )

    def test_list__sort__code(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.code)
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, True)

    def test_list__sort__fixed_fee(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.fixed_fee
        )
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "fixed_fee"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, True)

    def test_list__sort__name(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        product_shipping_list.sort(key=lambda product_shipping: product_shipping.name)
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "name"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, True)

    def test_list__sort__unit_fee(self):
        product_shipping_list = ProductShippingFactory.create_batch(
            2, organization_id=self.organization.id
        )
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee
        )
        product_shipping_dicts = [
            {"object": product_shipping, "product_dicts": []}
            for product_shipping in product_shipping_list
        ]
        path = reverse(
            "productshipping-list", kwargs={"organization_id": self.organization.id}
        )
        response = self.client.get(path, data={"ordering": "unit_fee"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_shipping_dicts, True)

    def test_partial_update(self):
        zones = faker.random_choices(
            elements=[choice[0] for choice in ZONE_CHOICES], length=3
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
            "products": [product.id for product in products[1:3]],
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
        product_shipping_dicts = [
            {
                "object": product_shipping,
                "product_dicts": [
                    {"object": product}
                    for product in self._create_and_set_products(product_shipping)
                ],
            }
        ]
        path = reverse(
            "productshipping-detail",
            kwargs={"organization_id": self.organization.id, "pk": product_shipping.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response([response.json()], product_shipping_dicts, False)

    def _assert_get_response(
        self, product_shipping_data_list, product_shipping_dicts, is_ordered
    ):
        if not is_ordered:
            product_shipping_data_list.sort(
                key=lambda product_shipping_data: product_shipping_data["id"]
            )
            product_shipping_dicts.sort(
                key=lambda product_shipping_dict: product_shipping_dict["object"].id
            )
        self.assertEqual(
            [
                product_shipping_data["id"]
                for product_shipping_data in product_shipping_data_list
            ],
            [
                product_shipping_dict["object"].id
                for product_shipping_dict in product_shipping_dicts
            ],
        )
        for index, product_shipping_data in enumerate(product_shipping_data_list):
            product_ids = product_shipping_data.pop("products")
            product_ids.sort()
            expected = [
                product_dict["object"].id
                for product_dict in product_shipping_dicts[index]["product_dicts"]
            ]
            expected.sort()
            self.assertEqual(product_ids, expected)
        product_shipping_list = [
            product_shipping_dict["object"]
            for product_shipping_dict in product_shipping_dicts
        ]
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
        self.assertEqual(product_shipping_data_list, expected)

    def _create_and_set_products(self, product_shipping):
        products = ProductFactory.create_batch(2, organization=self.organization)
        product_shipping.products.set(products)
        return products
