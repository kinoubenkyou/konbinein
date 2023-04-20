from django.db.models import F, OuterRef, Prefetch, Subquery, Sum
from rest_framework.viewsets import ModelViewSet

from main.filter_sets.order_filter_set import OrderFilterSet
from main.models.order import Order
from main.models.product_item import ProductItem
from main.permissions.staff_permission import StaffPermission
from main.serializers.order_serializer import OrderSerializer
from main.view_sets.filter_mixin import FilterMixin


class OrderViewSet(FilterMixin, ModelViewSet):
    filter_set_class = OrderFilterSet
    ordering_fields = ("code", "created_at", "id", "total")
    permission_classes = (StaffPermission,)
    queryset = (
        Order.objects.prefetch_related(
            Prefetch(
                "productitem_set",
                queryset=ProductItem.objects.annotate(total=F("quantity") * F("price")),
            )
        )
        .annotate(
            total=Subquery(
                Order.objects.annotate(
                    total=Sum(F("productitem__quantity") * F("productitem__price"))
                )
                .filter(id=OuterRef("pk"))
                .values("total")
            )
        )
        .distinct()
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
