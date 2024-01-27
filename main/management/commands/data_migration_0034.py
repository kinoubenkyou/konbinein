from django.core.management import BaseCommand
from django.db.models import Sum

from main.models.order import Order


class Command(BaseCommand):
    help = "Calculate order.product_shipping_total that are None"

    def add_arguments(self, parser):
        parser.add_argument(BATCH_SIZE, type=int)

    def handle(self, *args, **options):
        batch_size = options[BATCH_SIZE]
        query_set = Order.objects.filter(product_shipping_total=None)
        while query_set.count() > 0:
            orders = query_set[:batch_size]
            ids = [order.id for order in orders]
            data_list = (
                Order.objects.filter(id__in=ids)
                .values("id")
                .annotate(
                    product_shipping_total=Sum(
                        "productitem__productshippingitem__item_total"
                    )
                )
            )
            dict_ = {data["id"]: data["product_shipping_total"] for data in data_list}
            for order in orders:
                order.product_shipping_total = dict_[order.id]
            Order.objects.bulk_update(orders, ["product_shipping_total"])


BATCH_SIZE = "batch-size"
