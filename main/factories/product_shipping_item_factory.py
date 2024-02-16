from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from main.factories.product_item_factory import ProductItemFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.factories.shipping_item_factory import ShippingItemFactoryMixin
from main.models.product_shipping_item import ProductShippingItem


class ProductShippingItemFactory(ShippingItemFactoryMixin, DjangoModelFactory):
    class Meta:
        model = ProductShippingItem

    item_total = LazyAttribute(
        lambda product_shipping_item: product_shipping_item.fixed_fee
        + product_shipping_item.product_item.quantity * product_shipping_item.unit_fee
    )
    product_item = SubFactory(ProductItemFactory)
    product_shipping = SubFactory(ProductShippingFactory)
