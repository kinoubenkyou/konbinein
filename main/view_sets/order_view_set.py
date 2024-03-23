from drf_spectacular.utils import extend_schema
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from main.documents.order_activity import OrderActivity
from main.filter_sets.order_filter_set import OrderFilterSet
from main.models.order import Order
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.order_serializer import OrderSerializer
from main.shortcuts import ActivityType
from main.view_sets.create_mixin import CreateMixin
from main.view_sets.update_mixin import UpdateMixin


@extend_schema(tags=["organizations_orders"])
class OrderViewSet(
    CreateMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateMixin,
    GenericViewSet,
):
    activity_class = OrderActivity
    activity_type = ActivityType.ORGANIZATION
    filter_set_class = OrderFilterSet
    ordering_fields = (
        "code",
        "created_at",
        "id",
        "order_shipping_totalproduct_shipping_total",
        "product_total",
        "total",
    )
    permission_classes = (OrganizationPermission,)
    queryset = Order.objects.prefetch_related(
        "productitem_set__productshippingitem_set"
    ).all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
