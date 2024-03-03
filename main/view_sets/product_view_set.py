from drf_spectacular.utils import extend_schema

from main.documents.activity import ProductActivity
from main.filter_sets.product_filter_set import ProductFilterSet
from main.models.product import Product
from main.permissions.staff_permission import StaffPermission
from main.serializers.product_serializer import ProductSerializer
from main.view_sets.authenticated_view_set import AuthenticatedViewSet


@extend_schema(tags=["organizations_products"])
class ProductViewSet(AuthenticatedViewSet):
    activity_class = ProductActivity
    filter_set_class = ProductFilterSet
    ordering_fields = ("code", "id", "name", "price")
    permission_classes = (StaffPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
