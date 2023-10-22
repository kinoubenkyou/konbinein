from random import choice
from string import ascii_uppercase

from factory import Faker, LazyAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.order_factory import OrderFactory
from main.factories.product_factory import ProductFactory
from main.models.product_item import ProductItem


class ProductItemFactory(DjangoModelFactory):
    class Meta:
        model = ProductItem

    item_total = LazyAttribute(
        lambda product_item: product_item.price * product_item.quantity
    )
    name = Sequence(lambda n: f"name-{choice(ascii_uppercase)}{n}")
    order = SubFactory(OrderFactory)
    price = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    product = SubFactory(ProductFactory)
    quantity = Faker("pyint", max_value=100, min_value=1)
    shipping_total = Faker("pydecimal", left_digits=2, positive=True, right_digits=4)
    subtotal = LazyAttribute(lambda product_item: product_item.item_total)
    total = LazyAttribute(
        lambda product_item: product_item.subtotal + product_item.shipping_total
    )
