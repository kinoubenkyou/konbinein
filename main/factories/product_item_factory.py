from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.factories.order_factory import OrderFactory
from main.factories.product_factory import ProductFactory
from main.models.product_item import ProductItem


class ProductItemFactory(DjangoModelFactory):
    class Meta:
        model = ProductItem

    name = Sequence(lambda n: f"name{n}")
    order = SubFactory(OrderFactory)
    price = Faker("pydecimal", left_digits=2, positive=True, right_digits=2)
    product = SubFactory(ProductFactory)
    quantity = Faker("pyint", max_value=100, min_value=1)
