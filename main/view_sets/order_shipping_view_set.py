from drf_spectacular.utils import extend_schema
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from main.documents.order_shipping_activity import OrderShippingActivity
from main.filter_sets.order_shipping_filter_set import OrderShippingFilterSet
from main.models.order_shipping import OrderShipping
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.order_shipping_serializer import OrderShippingSerializer
from main.shortcuts import ActivityType
from main.view_sets.create_mixin import CreateMixin
from main.view_sets.update_mixin import UpdateMixin


@extend_schema(tags=["organizations_order_shippings"])
class OrderShippingViewSet(
    CreateMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateMixin,
    GenericViewSet,
):
    activity_class = OrderShippingActivity
    activity_type = ActivityType.ORGANIZATION
    filter_set_class = OrderShippingFilterSet
    ordering_fields = ("code", "fixed_fee", "id", "name", "unit_fee")
    permission_classes = (OrganizationPermission,)
    queryset = OrderShipping.objects.all()
    serializer_class = OrderShippingSerializer
