from drf_spectacular.utils import extend_schema
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from main.documents.product_shipping_activity import ProductShippingActivity
from main.filter_sets.product_shipping_filter_set import ProductShippingFilterSet
from main.models.product_shipping import ProductShipping
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.product_shipping_serializer import ProductShippingSerializer
from main.shortcuts import ActivityType
from main.view_sets.create_mixin import CreateMixin
from main.view_sets.update_mixin import UpdateMixin


@extend_schema(tags=["organizations_product_shippings"])
class ProductShippingViewSet(
    CreateMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateMixin,
    GenericViewSet,
):
    activity_class = ProductShippingActivity
    activity_type = ActivityType.ORGANIZATION
    filter_set_class = ProductShippingFilterSet
    ordering_fields = ("code", "fixed_fee", "id", "name", "unit_fee")
    permission_classes = (OrganizationPermission,)
    queryset = ProductShipping.objects.all()
    serializer_class = ProductShippingSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
