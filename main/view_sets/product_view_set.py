from rest_framework.viewsets import ModelViewSet

from main.filter_sets.product_filter_set import ProductFilterSet
from main.models.product import Product
from main.permissions.staff_permission import StaffPermission
from main.serializers.product_serializer import ProductSerializer
from main.view_sets.filter_mixin import FilterMixin


class ProductViewSet(FilterMixin, ModelViewSet):
    filter_set_class = ProductFilterSet
    ordering_fields = ("code", "name", "id", "price")
    permission_classes = (StaffPermission,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
