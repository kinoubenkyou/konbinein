from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet

from main.filter_sets.order_filter_set import OrderFilterSet
from main.models.order import Order
from main.permissions.staff_permission import StaffPermission
from main.serializers.order_serializer import OrderSerializer
from main.view_sets.filter_mixin import FilterMixin


@extend_schema(tags=["organizations_orders"])
class OrderViewSet(FilterMixin, ModelViewSet):
    filter_set_class = OrderFilterSet
    ordering_fields = (
        "code",
        "created_at",
        "id",
        "order_shipping_totalproduct_shipping_total",
        "product_total",
        "total",
    )
    permission_classes = (StaffPermission,)
    queryset = Order.objects.prefetch_related(
        "productitem_set__productshippingitem_set"
    ).all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
