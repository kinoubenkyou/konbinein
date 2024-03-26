from main.factories.shipping_factory import ShippingFactory
from main.models.product_shipping import ProductShipping


class ProductShippingFactory(ShippingFactory):
    class Meta:
        model = ProductShipping
