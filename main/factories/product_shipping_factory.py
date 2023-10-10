from factory.django import DjangoModelFactory

from main.factories.shipping_factory import ShippingFactoryMixin
from main.models.product_shipping import ProductShipping


class ProductShippingFactory(ShippingFactoryMixin, DjangoModelFactory):
    class Meta:
        model = ProductShipping
