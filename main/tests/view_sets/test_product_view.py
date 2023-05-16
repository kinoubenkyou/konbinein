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
from main.test_cases.staff_test_case import StaffTestCase
from main.tests import faker


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

    def test_list__filter__code__in(self):
        ProductFactory.create(organization=self.organization)
        products = ProductFactory.create_batch(2, organization=self.organization)
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"code__in": tuple(product.code for product in products)}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), products)

    def test_list__filter__name__in(self):
        ProductFactory.create(organization=self.organization)
        products = ProductFactory.create_batch(2, organization=self.organization)
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"name__in": tuple(product.name for product in products)}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), products)

    def test_list__filter__price__gte(self):
        prices = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=4)
            for _ in range(3)
        ]
        prices.sort(reverse=True)
        ProductFactory.create(organization=self.organization, price=prices.pop())
        products = ProductFactory.create_batch(
            2,
            organization=self.organization,
            price=Iterator(prices),
        )
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"price__gte": products[-1].price}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), products)

    def test_list__filter__price__lte(self):
        prices = [
            faker.pydecimal(left_digits=2, positive=True, right_digits=4)
            for _ in range(3)
        ]
        prices.sort()
        ProductFactory.create(organization=self.organization, price=prices.pop())
        products = ProductFactory.create_batch(
            2,
            organization=self.organization,
            price=Iterator(prices),
        )
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"price__lte": products[-1].price}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(response.json(), products)

    def test_list__paginate(self):
        products = ProductFactory.create_batch(4, organization_id=self.organization.id)
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        data = {"limit": 2, "offset": 1, "ordering": "id"}
        response = self.client.get(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        products.sort(key=lambda product: product.id)
        self._assertGetResponseData(
            response.json()["results"], (products[1], products[2]), is_ordered=True
        )

    def test_list__sort__code(self):
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "code"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        products.sort(key=lambda product: product.code)
        self._assertGetResponseData(response.json(), products, is_ordered=True)

    def test_list__sort__name(self):
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "name"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        products.sort(key=lambda product: product.name)
        self._assertGetResponseData(response.json(), products, is_ordered=True)

    def test_list__sort__price(self):
        products = ProductFactory.create_batch(2, organization_id=self.organization.id)
        path = reverse("product-list", kwargs={"organization_id": self.organization.id})
        response = self.client.get(path, data={"ordering": "price"}, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        products.sort(key=lambda product: product.price)
        self._assertGetResponseData(response.json(), products, is_ordered=True)

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
        path = reverse(
            "product-detail",
            kwargs={"organization_id": self.organization.id, "pk": product.id},
        )
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self._assertGetResponseData(
            (response.json(),),
            (product,),
        )

    def _assertGetResponseData(self, actual, products, is_ordered=False):
        expected = [
            {
                "code": product.code,
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
            }
            for product in products
        ]
        if is_ordered:
            self.assertEqual(actual, expected)
        else:
            self.assertCountEqual(actual, expected)
