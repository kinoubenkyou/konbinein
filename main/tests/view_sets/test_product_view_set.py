from factory import Iterator

from main.factories.product_factory import ProductFactory
from main.models.product import Product
from main.tests.view_sets.organization_test_case import OrganizationTestCase
from main.view_sets.product_view_set import ProductViewSet


class ProductViewSetTestCase(OrganizationTestCase):
    basename = "product"
    view_set = ProductViewSet

    def test_create(self):
        data = self._get_deserializer_data()
        self._act_and_assert_create_test(data, {**data})

    def test_create__code_already_in_another_product(self):
        product = ProductFactory.create(organization=self.organization)
        data = {**self._get_deserializer_data(), "code": product.code}
        self._act_and_assert_create_validation_test(
            data, {"code": ["Code is already in another product."]}
        )

    def test_destroy(self):
        self._act_and_assert_destroy_test(
            ProductFactory.create(organization=self.organization)
        )

    def test_list__filter__code__icontains(self):
        ProductFactory.create(organization=self.organization)
        ProductFactory.create_batch(
            2,
            code=Iterator(range(2), getter=lambda n: f"-code--{n}"),
            organization=self.organization,
        )
        self._act_and_assert_list_test({"code__icontains": "code--"})

    def test_list__filter__name__icontains(self):
        ProductFactory.create(organization=self.organization)
        ProductFactory.create_batch(
            2,
            name=Iterator(range(2), getter=lambda n: f"-name--{n}"),
            organization=self.organization,
        )
        self._act_and_assert_list_test({"name__icontains": "name--"})

    def test_list__filter__price__gte(self):
        products = ProductFactory.create_batch(3, organization=self.organization)
        products.sort(key=lambda product: product.price, reverse=True)
        self._act_and_assert_list_test({"price__gte": products[1].price})

    def test_list__filter__price__lte(self):
        products = ProductFactory.create_batch(3, organization=self.organization)
        products.sort(key=lambda product: product.price)
        self._act_and_assert_list_test({"price__lte": products[1].price})

    def test_list__paginate(self):
        ProductFactory.create_batch(4, organization=self.organization)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__code(self):
        ProductFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "code"})

    def test_list__sort__name(self):
        ProductFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "name"})

    def test_list__sort__price(self):
        ProductFactory.create_batch(2, organization_id=self.organization.id)
        self._act_and_assert_list_test({"ordering": "price"})

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(
            ProductFactory.create(organization=self.organization).id
        )

    def test_update(self):
        product = ProductFactory.create(organization_id=self.organization.id)
        data = self._get_deserializer_data()
        filter_ = {**data, "organization_id": self.organization.id}
        self._act_and_assert_update_test(data, filter_, product.id)

    @staticmethod
    def _get_deserializer_data():
        product = ProductFactory.build()
        return {
            "code": product.code,
            "name": product.name,
            "price": str(product.price),
        }

    def _get_query_set(self):
        return Product.objects.filter(organization=self.organization.id)

    @staticmethod
    def _get_serializer_data(product):
        return {
            "code": product.code,
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
        }
