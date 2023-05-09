from django.core.management import BaseCommand
from django.db.models import F, Sum

from main.models.order import Order
from main.models.product_item import ProductItem


class Command(BaseCommand):
    help = "Calculate and update product item total and order total that are None."

    def add_arguments(self, parser):
        parser.add_argument(ARGUMENT_NAME, type=int)

    def handle(self, *args, **options):
        batch_size = options[ARGUMENT_NAME]
        query_set = ProductItem.objects.filter(total=None).order_by("id")
        while query_set.count() > 0:
            product_items = tuple(query_set[:batch_size])
            ids = tuple(product_item.id for product_item in product_items)
            data_list = (
                ProductItem.objects.filter(id__in=ids)
                .values("id")
                .annotate(total=F("price") * F("quantity"))
            )
            total_dict = {data["id"]: data["total"] for data in data_list}
            for product_item in product_items:
                product_item.total = total_dict[product_item.id]
            ProductItem.objects.bulk_update(product_items, ["total"])
        query_set = Order.objects.filter(total=None).order_by("id")
        while query_set.count() > 0:
            orders = tuple(query_set[:batch_size])
            ids = tuple(order.id for order in orders)
            data_list = (
                Order.objects.filter(id__in=ids)
                .values("id")
                .annotate(
                    total=Sum(F("productitem__price") * F("productitem__quantity"))
                )
            )
            total_dict = {data["id"]: data["total"] for data in data_list}
            for order in orders:
                order.total = total_dict[order.id]
            Order.objects.bulk_update(orders, ["total"])


ARGUMENT_NAME = "batch-size"
