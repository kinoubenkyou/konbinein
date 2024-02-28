from main.factories.product_factory import ProductFactory
from main.factories.product_shipping_factory import ProductShippingFactory


class ProductShippingWithRelatedFactory:
    def __init__(
        self,
        products=None,
        product_count=0,
        product_kwargs=None,
        product_shipping_kwargs=None,
    ):
        self.products = products or ProductFactory.build_batch(
            product_count, **product_kwargs or {}
        )
        self.product_shipping_kwargs = product_shipping_kwargs

    def create(self):
        product_shipping = self._build()
        product_shipping.save()
        for product in product_shipping.cached_products:
            product.save()
        product_shipping.products.set(product_shipping.cached_products)
        return product_shipping

    def create_batch(self, product_shipping_count):
        return [self.create() for _ in range(product_shipping_count)]

    def get_deserializer_data(self):
        product_shipping = self._build()
        for product in product_shipping.cached_products:
            product.save()
        return {
            "code": product_shipping.code,
            "fixed_fee": str(product_shipping.fixed_fee),
            "name": product_shipping.name,
            "products": [product.id for product in product_shipping.cached_products],
            "unit_fee": str(product_shipping.unit_fee),
            "zones": product_shipping.zones,
        }

    def _build(self):
        product_shipping = ProductShippingFactory.build(
            **self.product_shipping_kwargs or {}
        )
        product_shipping.cached_products = self.products
        return product_shipping
