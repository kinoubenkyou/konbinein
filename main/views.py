from django.db.models import F, Prefetch, Sum
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
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

    @action(detail=True, methods=["post"])
    def email_verification(self, request, *args, **kwargs):
        user = self.get_object()
        token = user.email_verification_token
        if token is None:
            raise NotFound(
                code="email_already_verified", detail="Email is already verified."
            )
        if request.data.get("token") == token:
            user.email_verification_token = None
            user.save()
            return Response(status=HTTP_204_NO_CONTENT)
        raise ParseError(code="token_not_match", detail="Token doesn't match.")
