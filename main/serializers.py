from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils.http import urlencode
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DecimalField, IntegerField
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

from main.models import Order, OrderItem, Organization, User


class OrderItemSerializer(ModelSerializer):
    id = IntegerField(required=False)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ["id", "name", "quantity", "total", "unit_price"]
        model = OrderItem


class OrderSerializer(ModelSerializer):
    orderitem_set = OrderItemSerializer(allow_empty=False, many=True)
    total = DecimalField(
        decimal_places=4, max_digits=19, read_only=True, source="self.total"
    )

    class Meta:
        fields = ["code", "created_at", "id", "orderitem_set", "organization", "total"]
        model = Order

    @transaction.atomic
    def create(self, validated_data):
        data_list = validated_data.pop("orderitem_set", [])
        order = super().create(validated_data)
        for data in data_list:
            OrderItemSerializer().create(data | {"order": order})
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        data_list = validated_data.pop("orderitem_set", [])
        super().update(instance, validated_data)
        order_item_dict = {
            order_item.id: order_item for order_item in instance.orderitem_set.all()
        }
        for data in data_list:
            _id = data.get("id", None)
            if _id is None:
                OrderItemSerializer().create(data | {"order": instance})
            else:
                OrderItemSerializer().update(order_item_dict[_id], data)
        for _id, order_item in order_item_dict.items():
            if _id not in (data.get("id", None) for data in data_list):
                order_item.delete()
        return instance


class OrganizationSerializer(ModelSerializer):
    class Meta:
        fields = ["id", "name"]
        model = Organization


class UserSerializer(ModelSerializer):
    password = CharField(max_length=255, write_only=True)
    current_password = CharField(max_length=255, required=False, write_only=True)

    class Meta:
        fields = ["email", "id", "name", "password", "current_password"]
        model = User

    @staticmethod
    def _modify_to_attributes(validated_data):
        if "current_password" in validated_data:
            del validated_data["current_password"]
        if "email" in validated_data:
            validated_data["email_verification_token"] = Token.generate_key()
        if "password" in validated_data:
            password = validated_data.pop("password")
            validated_data["hashed_password"] = make_password(password)

    def _send_email_verification(self, user):
        if user.email_verification_token is not None:
            uri_path = reverse(
                "user-email-verification",
                kwargs={"pk": user.id},
                request=self.context["request"],
            )
            query = urlencode({"token": user.email_verification_token})
            send_mail(
                from_email=None,
                message=f"{uri_path}?{query}",
                recipient_list=[user.email],
                subject="Konbinein Email Verification",
            )

    @transaction.atomic
    def create(self, validated_data):
        self._modify_to_attributes(validated_data)
        user = super().create(validated_data)
        self._send_email_verification(user)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        self._modify_to_attributes(validated_data)
        user = super().update(instance, validated_data)
        self._send_email_verification(user)
        return instance

    def validate(self, attrs):
        if self.instance is not None and ("password" in attrs or "email" in attrs):
            if "current_password" not in attrs:
                raise ValidationError(
                    "Current password is required.", "current_password_required"
                )
            if not check_password(
                attrs["current_password"], self.instance.hashed_password
            ):
                raise ValidationError(
                    "Current password is incorrect.", "current_password_incorrect"
                )
        return attrs
