from django.db.models import F, Prefetch, Sum
from rest_framework.viewsets import ModelViewSet

from main.models import Order, OrderItem, Organization, User
from main.serializers import OrderSerializer, OrganizationSerializer, UserSerializer


class OrderViewSet(ModelViewSet):
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


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
