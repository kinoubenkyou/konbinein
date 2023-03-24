from django.db.models import F, Prefetch, Sum
from rest_framework.viewsets import ModelViewSet

from main.models.order import Order
from main.models.order_item import OrderItem
from main.permissions.organization_permission import OrganizationPermission
from main.serializers.order_serializer import OrderSerializer


class OrderViewSet(ModelViewSet):
    permission_classes = (OrganizationPermission,)
    queryset = (
        Order.objects.prefetch_related(
            Prefetch(
                "orderitem_set",
                queryset=OrderItem.objects.annotate(
                    total=F("quantity") * F("unit_price")
                ),
            )
        )
        .annotate(total=Sum(F("orderitem__quantity") * F("orderitem__unit_price")))
        .all()
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(organization=self.kwargs["organization_id"])
        )
