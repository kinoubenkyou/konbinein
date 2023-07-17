from factory import Iterator
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from main.factories.product_factory import ProductFactory
from main.models.product import Product
from main.tests.staff_test_case import StaffTestCase


class ProductViewSetTestCase(StaffTestCase):
    def test_create(self):
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        built_product = ProductFactory.build()
        data = {
            "code": built_product.code,
            "name": built_product.name,
            "price": built_product.price,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        filter_ = {**data, "organization_id": self.organization.id}
        product = Product.objects.filter(**filter_).first()
        self.assertIsNotNone(product)

    def test_create__code_already_in_another_product(self):
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        product = ProductFactory.create(organization=self.organization)
        built_product = ProductFactory.build(organization=self.organization)
        data = {
            "code": product.code,
            "name": built_product.name,
            "price": built_product.price,
        }
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), {"code": ["Code is already in another product."]}
        )

    def test_destroy(self):
        product = ProductFactory.create(organization=self.organization)
        path = reverse(
            "product-detail",
            kwargs={"organization_id": self.organization.id, "pk": product.id},
        )
        response = self.client.delete(path, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_list__filter__code__icontains(self):
        ProductFactory.create(organization=self.organization)
        product_dicts = [
            {"object": product}
            for product in ProductFactory.create_batch(
                2,
                code=Iterator(range(2), getter=lambda n: f"-code-{n}"),
                organization=self.organization,
            )
        ]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"code__icontains": "code-"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, False)

    def test_list__filter__name__icontains(self):
        ProductFactory.create(organization=self.organization)
        product_dicts = [
            {"object": product}
            for product in ProductFactory.create_batch(
                2,
                name=Iterator(range(2), getter=lambda n: f"-name-{n}"),
                organization=self.organization,
            )
        ]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"name__icontains": "name-"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, False)

    def test_list__filter__price__gte(self):
        products = ProductFactory.create_batch(2, organization=self.organization)
        products.sort(key=lambda product: product.price, reverse=True)
        products.pop()
        product_dicts = [{"object": product} for product in products]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"price__gte": products[-1].price}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, False)

    def test_list__filter__price__lte(self):
        products = ProductFactory.create_batch(2, organization=self.organization)
        products.sort(key=lambda product: product.price)
        products.pop()
        product_dicts = [{"object": product} for product in products]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"price__lte": products[-1].price}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, False)

    def test_list__paginate(self):
        products = ProductFactory.create_batch(4, organization_id=self.organization.id)
        products.sort(key=lambda product: product.id)
        product_dicts = [{"object": product} for product in products[1:3]]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json()["results"], product_dicts, True)

    def test_list__sort__code(self):
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        products.sort(key=lambda product: product.code)
        product_dicts = [{"object": product} for product in products]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, True)

    def test_list__sort__name(self):
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        products.sort(key=lambda product: product.name)
        product_dicts = [{"object": product} for product in products]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "name"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, True)

    def test_list__sort__price(self):
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        products.sort(key=lambda product: product.price)
        product_dicts = [{"object": product} for product in products]
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "price"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response(response.json(), product_dicts, True)

    def test_partial_update(self):
        product = ProductFactory.create(organization_id=self.organization.id)
        built_product = ProductFactory.build()
        path = reverse(
            "product-detail",
            kwargs={"organization_id": self.organization.id, "pk": product.id},
        )
        data = {
            "code": built_product.code,
            "name": built_product.name,
            "price": built_product.price,
        }
        response = self.client.patch(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        filter_ = {**data, "id": product.id, "organization_id": self.organization.id}
        self.assertTrue(Product.objects.filter(**filter_).exists())

    def test_retrieve(self):
        product = ProductFactory.create(organization_id=self.organization.id)
        product_dicts = [{"object": product}]
        path = reverse(
            "product-detail",
            kwargs={"organization_id": self.organization.id, "pk": product.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assert_get_response([response.json()], product_dicts, False)

    def _assert_get_response(self, product_data_list, product_dicts, is_ordered):
        if not is_ordered:
            product_data_list.sort(key=lambda product_data: product_data["id"])
            product_dicts.sort(key=lambda product_dict: product_dict["object"].id)
        products = [product_dict["object"] for product_dict in product_dicts]
        expected = [
            {
                "code": product.code,
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
            }
            for product in products
        ]
        self.assertEqual(product_data_list, expected)
