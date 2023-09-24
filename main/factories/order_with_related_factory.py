from main.factories.order_factory import OrderFactory
from main.factories.product_factory import ProductFactory
from main.factories.product_item_factory import ProductItemFactory
from main.factories.product_shipping_factory import ProductShippingFactory
from main.factories.product_shipping_item_factory import ProductShippingItemFactory


class OrderWithRelatedFactory:
    @classmethod
    def create(
        cls,
        order_kwargs=None,
        product=None,
        product_item_count=0,
        product_kwargs=None,
        product_shipping=None,
        product_shipping_item_count=0,
        product_shipping_kwargs=None,
    ):
        order = cls._build(
            order_kwargs,
            product,
            product_item_count,
            product_kwargs,
            product_shipping,
            product_shipping_item_count,
            product_shipping_kwargs,
        )
        order.save()
        for product_item in order.product_items:
            product_item.product.save()
            product_item.save()
            for product_shipping_item in product_item.product_shipping_items:
                product_shipping_item.product_shipping.save()
                product_shipping_item.save()
        return order

    @classmethod
    def create_data(
        cls,
        order_kwargs=None,
        product=None,
        product_item_count=0,
        product_kwargs=None,
        product_shipping=None,
        product_shipping_item_count=0,
        product_shipping_kwargs=None,
    ):
        order = cls._build(
            order_kwargs,
            product,
            product_item_count,
            product_kwargs,
            product_shipping,
            product_shipping_item_count,
            product_shipping_kwargs,
        )
        for product_item in order.product_items:
            product_item.product.save()
            for product_shipping_item in product_item.product_shipping_items:
                product_shipping_item.product_shipping.save()
        return {
            "code": order.code,
            "created_at": order.created_at,
            "productitem_set": [
                cls._create_product_item_data(product_item)
                for product_item in order.product_items
            ],
            "product_total": order.product_total,
            "total": order.total,
        }

    @staticmethod
    def _build(
        order_kwargs,
        product,
        product_item_count,
        product_kwargs,
        product_shipping,
        product_shipping_item_count,
        product_shipping_kwargs,
    ):
        order = OrderFactory.build(**order_kwargs or {})
        order.product_items = ProductItemFactory.build_batch(
            product_item_count,
            order=order,
            product=product or ProductFactory.build(**product_kwargs or {}),
        )
        for product_item in order.product_items:
            product_item.product_shipping_items = (
                ProductShippingItemFactory.build_batch(
                    product_shipping_item_count,
                    product_item=product_item,
                    product_shipping=product_shipping
                    or ProductShippingFactory.build(**product_shipping_kwargs or {}),
                )
            )
            product_item.shipping_total = sum(
                product_shipping_item.total
                for product_shipping_item in product_item.product_shipping_items
            )
            product_item.subtotal = product_item.item_total
            product_item.total = product_item.subtotal + product_item.shipping_total
        order.product_total = sum(
            product_item.total for product_item in order.product_items
        )
        order.total = order.product_total
        return order

    @classmethod
    def _create_product_item_data(cls, product_item):
        return {
            "name": product_item.name,
            "item_total": product_item.item_total,
            "price": product_item.price,
            "product": product_item.product.id,
            "productshippingitem_set": [
                cls._create_product_shipping_item_data(product_shipping_item)
                for product_shipping_item in product_item.product_shipping_items
            ],
            "quantity": product_item.quantity,
            "shipping_total": product_item.shipping_total,
            "subtotal": product_item.subtotal,
            "total": product_item.total,
        }

    @staticmethod
    def _create_product_shipping_item_data(product_shipping_item):
        return {
            "fixed_fee": product_shipping_item.fixed_fee,
            "item_total": product_shipping_item.item_total,
            "name": product_shipping_item.name,
            "product_shipping": product_shipping_item.product_shipping.id,
            "subtotal": product_shipping_item.subtotal,
            "total": product_shipping_item.total,
            "unit_fee": product_shipping_item.unit_fee,
        }
