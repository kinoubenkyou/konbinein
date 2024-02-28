from main.factories.order_factory import OrderFactory
from main.factories.order_shipping_factory import OrderShippingFactory
from main.factories.order_shipping_item_factory import OrderShippingItemFactory
from main.factories.product_factory import ProductFactory
from main.factories.product_item_factory import ProductItemFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.factories.product_shipping_item_factory import ProductShippingItemFactory


class OrderWithRelatedFactory:
    def __init__(
        self,
        order_kwargs=None,
        order_shipping=None,
        order_shipping_item_count=0,
        order_shipping_kwargs=None,
        product=None,
        product_item_count=0,
        product_kwargs=None,
        product_shipping=None,
        product_shipping_item_count=0,
        product_shipping_kwargs=None,
    ):
        self.order_kwargs = order_kwargs
        self.order_shipping = order_shipping or OrderShippingFactory.build(
            **order_shipping_kwargs or {}
        )
        self.order_shipping_item_count = order_shipping_item_count
        self.product = product or ProductFactory.build(**product_kwargs or {})
        self.product_item_count = product_item_count
        self.product_shipping = product_shipping or ProductShippingFactory.build(
            **product_shipping_kwargs or {}
        )
        self.product_shipping_item_count = product_shipping_item_count

    def create(self):
        order = self._build()
        order.save()
        self._create_order_shipping_item(order)
        self._create_product_item(order)
        return order

    def create_batch(self, order_count):
        return [self.create() for _ in range(order_count)]

    def get_deserializer_data(self):
        order = self._build()
        return {
            "code": order.code,
            "created_at": str(order.created_at),
            "order_shipping_total": str(order.order_shipping_total),
            "ordershippingitem_set": [
                self._get_deserializer_order_shipping_item_data(order_shipping_item)
                for order_shipping_item in order.cached_order_shipping_items
            ],
            "product_shipping_total": str(order.product_shipping_total),
            "product_total": str(order.product_total),
            "productitem_set": [
                self._get_deserializer_product_item_data(product_item)
                for product_item in order.cached_product_items
            ],
            "total": str(order.total),
        }

    def _build(self):
        order = OrderFactory.build(**self.order_kwargs or {})
        self._build_product_item(order)
        self._build_order_shipping_item(order)
        order.order_shipping_total = sum(
            order_shipping_item.item_total
            for order_shipping_item in order.cached_order_shipping_items
        )
        order.product_total = sum(
            product_item.item_total for product_item in order.cached_product_items
        )
        order.product_shipping_total = sum(
            product_shipping_item.item_total
            for product_item in order.cached_product_items
            for product_shipping_item in product_item.cached_product_shipping_items
        )
        order.total = (
            order.order_shipping_total
            + order.product_total
            + order.product_shipping_total
        )
        return order

    def _build_order_shipping_item(self, order):
        order.cached_order_shipping_items = OrderShippingItemFactory.build_batch(
            self.order_shipping_item_count,
            order=order,
            order_shipping=self.order_shipping,
        )
        for order_shipping_item in order.cached_order_shipping_items:
            order_shipping_item.item_total = (
                order_shipping_item.fixed_fee
                + len(order.cached_product_items) * order_shipping_item.unit_fee
            )

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
    def _create_order_shipping_item(cls, order):
        for order_shipping_item in order.cached_order_shipping_items:
            order_shipping_item.order_shipping.save()
            order_shipping_item.save()

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

    @staticmethod
    def _get_deserializer_order_shipping_item_data(order_shipping_item):
        order_shipping_item.order_shipping.save()
        return {
            "fixed_fee": str(order_shipping_item.fixed_fee),
            "item_total": str(order_shipping_item.item_total),
            "name": order_shipping_item.name,
            "order_shipping": order_shipping_item.order_shipping.id,
            "unit_fee": str(order_shipping_item.unit_fee),
        }

    @classmethod
    def _get_deserializer_product_item_data(cls, product_item):
        product_item.product.save()
        return {
            "item_total": str(product_item.item_total),
            "name": product_item.name,
            "price": str(product_item.price),
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
            "fixed_fee": str(product_shipping_item.fixed_fee),
            "item_total": str(product_shipping_item.item_total),
            "name": product_shipping_item.name,
            "product_shipping": product_shipping_item.product_shipping.id,
            "unit_fee": str(product_shipping_item.unit_fee),
        }
