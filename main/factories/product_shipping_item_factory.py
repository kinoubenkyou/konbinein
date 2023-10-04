from factory import Faker, LazyAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.product_item_factory import ProductItemFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.models.product_shipping_item import ProductShippingItem


class ProductShippingItemFactory(DjangoModelFactory):
    class Meta:
        model = ProductShippingItem

    fixed_fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    item_total = LazyAttribute(
        lambda product_shipping_item: product_shipping_item.fixed_fee
        + product_shipping_item.product_item.quantity * product_shipping_item.unit_fee
    )
    name = Sequence(lambda n: f"name{n}")
    product_item = SubFactory(ProductItemFactory)
    product_shipping = SubFactory(ProductShippingFactory)
    subtotal = LazyAttribute(
        lambda product_shipping_item: product_shipping_item.item_total
    )
    total = LazyAttribute(lambda product_shipping_item: product_shipping_item.subtotal)
    unit_fee = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)