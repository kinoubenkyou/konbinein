from main.filter_sets.order_filter_set import OrderFilterSet
from main.models.order import Order
from main.permissions.staff_permission import StaffPermission
from main.serializers.order_serializer import OrderSerializer
from main.views.filterable_model_view_set import FilterableModelViewSet


class OrderViewSet(FilterableModelViewSet):
    filter_set_class = OrderFilterSet
    permission_classes = (StaffPermission,)
    queryset = Order.objects.prefetch_related("orderitem_set").distinct()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
