from main.factories.order_factory import OrderFactory
from main.factories.product_factory import ProductFactory
from main.factories.product_item_factory import ProductItemFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.factories.product_shipping_item_factory import ProductShippingItemFactory


class OrderWithRelatedFactory:
    def __init__(
        self,
        order_kwargs=None,
        product=None,
        product_item_count=0,
        product_kwargs=None,
        product_shipping=None,
        product_shipping_item_count=0,
        product_shipping_kwargs=None,
    ):
        self.order_kwargs = order_kwargs
        self.product = product or ProductFactory.build(**product_kwargs or {})
        self.product_item_count = product_item_count
        self.product_shipping = product_shipping or ProductShippingFactory.build(
            **product_shipping_kwargs or {}
        )
        self.product_shipping_item_count = product_shipping_item_count

    def create(self):
        order = self._build()
        order.save()
        self._create_product_item(order)
        return order

    def create_batch(self, order_count):
        return [self.create() for _ in range(order_count)]

    def get_deserializer_data(self):
        order = self._build()
        return {
            "code": order.code,
            "created_at": order.created_at,
            "product_shipping_total": order.product_shipping_total,
            "product_total": order.product_total,
            "productitem_set": [
                self._get_deserializer_product_item_data(product_item)
                for product_item in order.cached_product_items
            ],
            "total": order.total,
        }

    def _build(self):
        order = OrderFactory.build(**self.order_kwargs or {})
        self._build_product_item(order)
        order.product_total = sum(
            product_item.item_total for product_item in order.cached_product_items
        )
        order.product_shipping_total = sum(
            product_shipping_item.item_total
            for product_item in order.cached_product_items
            for product_shipping_item in product_item.cached_product_shipping_items
        )
        order.total = order.product_total + order.product_shipping_total
        return order

    def _build_product_item(self, order):
        order.cached_product_items = ProductItemFactory.build_batch(
            self.product_item_count,
            order=order,
            product=self.product,
        )
        for product_item in order.cached_product_items:
            self._build_product_shipping_item(product_item)

    def _build_product_shipping_item(self, product_item):
        product_item.cached_product_shipping_items = (
            ProductShippingItemFactory.build_batch(
                self.product_shipping_item_count,
                product_item=product_item,
                product_shipping=self.product_shipping,
            )
        )

    @classmethod
    def _create_product_item(cls, order):
        for product_item in order.cached_product_items:
            product_item.product.save()
            product_item.save()
            cls._create_product_shipping_item(product_item)

    @staticmethod
    def _create_product_shipping_item(product_item):
        for product_shipping_item in product_item.cached_product_shipping_items:
            product_shipping_item.product_shipping.save()
            product_shipping_item.save()

    @classmethod
    def _get_deserializer_product_item_data(cls, product_item):
        product_item.product.save()
        return {
            "name": product_item.name,
            "item_total": product_item.item_total,
            "price": product_item.price,
            "product": product_item.product.id,
            "productshippingitem_set": [
                cls._get_deserializer_product_shipping_item_data(product_shipping_item)
                for product_shipping_item in product_item.cached_product_shipping_items
            ],
            "quantity": product_item.quantity,
        }

    @staticmethod
    def _get_deserializer_product_shipping_item_data(product_shipping_item):
        product_shipping_item.product_shipping.save()
        return {
            "fixed_fee": product_shipping_item.fixed_fee,
            "item_total": product_shipping_item.item_total,
            "name": product_shipping_item.name,
            "product_shipping": product_shipping_item.product_shipping.id,
            "unit_fee": product_shipping_item.unit_fee,
        }
