from drf_spectacular.utils import extend_schema

from main.documents.activity import ProductShippingActivity
from main.filter_sets.product_shipping_filter_set import ProductShippingFilterSet
from main.models.product_shipping import ProductShipping
from main.permissions.staff_permission import StaffPermission
from main.serializers.product_shipping_serializer import ProductShippingSerializer
from main.view_sets.authenticated_view_set import AuthenticatedViewSet
from main.view_sets.filter_mixin import FilterMixin


@extend_schema(tags=["organizations_product_shippings"])
class ProductShippingViewSet(FilterMixin, AuthenticatedViewSet):
    activity_class = ProductShippingActivity
    filter_set_class = ProductShippingFilterSet
    ordering_fields = ("code", "fixed_fee", "id", "name", "unit_fee")
    permission_classes = (StaffPermission,)
    queryset = ProductShipping.objects.all()
    serializer_class = ProductShippingSerializer
