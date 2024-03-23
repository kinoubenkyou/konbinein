from random import sample

from factory import Iterator

from main.factories.product_factory import ProductFactory
from main.factories.product_shipping_with_related_factory import (
    ProductShippingWithRelatedFactory,
)
from main.models import ZONE_CHOICES
from main.models.product import Product
from main.models.product_shipping import ProductShipping
from main.tests.view_sets.organization_test_case import OrganizationTestCase
from main.view_sets.product_shipping_view_set import ProductShippingViewSet


class ProductShippingViewSetTestCase(OrganizationTestCase):
    basename = "productshipping"
    view_set = ProductShippingViewSet

    def test_create(self):
        data = ProductShippingWithRelatedFactory(
            product_count=2,
            product_kwargs={"organization_id": self.organization.id},
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).get_deserializer_data()
        filter_ = {**data, "organization_id": self.organization.id}
        self._act_and_assert_create_test(data, filter_)

    def test_create__code_already_in_another_product_shipping(self):
        product_shipping = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create()
        data = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).get_deserializer_data()
        data["code"] = product_shipping.code
        self._act_and_assert_create_validation_test(
            data, {"code": ["Code is already in another product shipping."]}
        )

    def test_create__products_in_another_organizations(self):
        data = ProductShippingWithRelatedFactory(
            products=ProductFactory.create_batch(2),
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).get_deserializer_data()
        self._act_and_assert_create_validation_test(
            data, {"products": ["Products are in another organization."]}
        )

    def test_destroy(self):
        product_shipping = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization": self.organization}
        ).create()
        self._act_and_assert_destroy_test(product_shipping)

    def test_list__filter__code__icontains(self):
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create()
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={
                "code": Iterator(range(2), getter=lambda n: f"-code--{n}"),
                "organization_id": self.organization.id,
            },
        ).create_batch(2)
        self._act_and_assert_list_test({"code__icontains": "code--"})

    def test_list__filter__fixed_fee__gte(self):
        product_shipping_list = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(3)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.fixed_fee, reverse=True
        )
        self._act_and_assert_list_test({
            "fixed_fee__gte": product_shipping_list[1].fixed_fee
        })

    def test_list__filter__fixed_fee__lte(self):
        product_shipping_list = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(3)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.fixed_fee
        )
        self._act_and_assert_list_test({
            "fixed_fee__lte": product_shipping_list[1].fixed_fee
        })

    def test_list__filter__name__icontains(self):
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create()
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={
                "name": Iterator(range(2), getter=lambda n: f"-name--{n}"),
                "organization_id": self.organization.id,
            },
        ).create_batch(2)
        self._act_and_assert_list_test({"name__icontains": "name--"})

    def test_list__filter__unit_fee__gte(self):
        product_shipping_list = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(3)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee, reverse=True
        )
        self._act_and_assert_list_test({
            "unit_fee__gte": product_shipping_list[1].unit_fee
        })

    def test_list__filter__unit_fee__lte(self):
        product_shipping_list = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(3)
        product_shipping_list.sort(
            key=lambda product_shipping: product_shipping.unit_fee
        )
        self._act_and_assert_list_test({
            "unit_fee__lte": product_shipping_list[1].unit_fee
        })

    def test_list__filter__products__in(self):
        ProductShippingWithRelatedFactory(
            product_count=2,
            product_kwargs={"organization_id": self.organization.id},
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create()
        product_shipping_list = ProductShippingWithRelatedFactory(
            product_count=2,
            product_kwargs={"organization_id": self.organization.id},
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(2)
        self._act_and_assert_list_test({
            "products__in": [
                product_shipping.products.all()[0].id
                for product_shipping in product_shipping_list
            ]
        })

    def test_list__filter__zones__overlap(self):
        zones = sample([choice[0] for choice in ZONE_CHOICES], 6)
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={
                "organization_id": self.organization.id,
                "zones": zones[0:2],
            },
        ).create()
        product_shipping_list = ProductShippingWithRelatedFactory(
            product_shipping_kwargs={
                "organization_id": self.organization.id,
                "zones": Iterator([zones[2:4], zones[4:6]]),
            },
        ).create_batch(2)
        self._act_and_assert_list_test({
            "zones__overlap": [
                product_shipping.zones[0] for product_shipping in product_shipping_list
            ]
        })

    def test_list__paginate(self):
        ProductShippingWithRelatedFactory(
            product_count=2,
            product_kwargs={"organization_id": self.organization.id},
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(4)
        self._act_and_assert_list_test({"limit": 2, "offset": 1, "ordering": "id"})

    def test_list__sort__code(self):
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "code"})

    def test_list__sort__fixed_fee(self):
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "fixed_fee"})

    def test_list__sort__name(self):
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "name"})

    def test_list__sort__unit_fee(self):
        ProductShippingWithRelatedFactory(
            product_shipping_kwargs={"organization_id": self.organization.id},
        ).create_batch(2)
        self._act_and_assert_list_test({"ordering": "unit_fee"})

    def test_retrieve(self):
        self._act_and_assert_retrieve_test(
            ProductShippingWithRelatedFactory(
                product_count=2,
                product_kwargs={"organization_id": self.organization.id},
                product_shipping_kwargs={"organization_id": self.organization.id},
            )
            .create()
            .id
        )

    def test_update(self):
        products = ProductFactory.create_batch(3, organization=self.organization)
        zones = sample([choice[0] for choice in ZONE_CHOICES], 3)
        product_shipping = ProductShippingWithRelatedFactory(
            products=products[0:2],
            product_shipping_kwargs={
                "organization_id": self.organization.id,
                "zones": zones[0:2],
            },
        ).create()
        data = ProductShippingWithRelatedFactory(
            products=products[1:3],
            product_shipping_kwargs={
                "organization_id": self.organization.id,
                "zones": zones[1:3],
            },
        ).get_deserializer_data()
        filter_ = {**data, "organization_id": self.organization.id}
        self._act_and_assert_update_test(data, filter_, product_shipping.id)

    def _assert_saved_object(self, filter_):
        product_ids = filter_.pop("products")
        product_shippings = list(ProductShipping.objects.filter(**filter_))
        self.assertEqual(len(product_shippings), 1)
        self.assertCountEqual(
            Product.objects.filter(productshipping=product_shippings[0].id).values_list(
                "id", flat=True
            ),
            product_ids,
        )

    @staticmethod
    def _serializer_data(product_shipping):
        product_ids = [product.id for product in product_shipping.products.all()]
        product_ids.sort()
        return {
            "code": product_shipping.code,
            "fixed_fee": str(product_shipping.fixed_fee),
            "id": product_shipping.id,
            "name": product_shipping.name,
            "products": product_ids,
            "unit_fee": str(product_shipping.unit_fee),
            "zones": product_shipping.zones,
        }
