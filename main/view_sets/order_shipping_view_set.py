from drf_spectacular.utils import extend_schema

from main.documents.activity import OrderShippingActivity
from main.filter_sets.order_shipping_filter_set import OrderShippingFilterSet
from main.models.order_shipping import OrderShipping
from main.permissions.staff_permission import StaffPermission
from main.serializers.order_shipping_serializer import OrderShippingSerializer
from main.view_sets.authenticated_view_set import AuthenticatedViewSet
from main.view_sets.filter_mixin import FilterMixin


@extend_schema(tags=["organizations_order_shippings"])
class OrderShippingViewSet(FilterMixin, AuthenticatedViewSet):
    activity_class = OrderShippingActivity
    filter_set_class = OrderShippingFilterSet
    ordering_fields = ("code", "fixed_fee", "id", "name", "unit_fee")
    permission_classes = (StaffPermission,)
    queryset = OrderShipping.objects.all()
    serializer_class = OrderShippingSerializer
