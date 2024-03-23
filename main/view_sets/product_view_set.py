from drf_spectacular.utils import extend_schema
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from main.documents.product_activity import ProductActivity
from main.filter_sets.product_filter_set import ProductFilterSet
from main.models.product import Product
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.product_serializer import ProductSerializer
from main.shortcuts import ActivityType
from main.view_sets.create_mixin import CreateMixin
from main.view_sets.update_mixin import UpdateMixin


@extend_schema(tags=["organizations_products"])
class ProductViewSet(
    CreateMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateMixin,
    GenericViewSet,
):
    activity_class = ProductActivity
    activity_type = ActivityType.ORGANIZATION
    filter_set_class = ProductFilterSet
    ordering_fields = ("code", "id", "name", "price")
    permission_classes = (OrganizationPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
