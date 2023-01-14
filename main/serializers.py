from django.contrib.auth.hashers import make_password
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
    password_confirmation = CharField(max_length=255, write_only=True)

    class Meta:
        fields = ["email", "id", "name", "password", "password_confirmation"]
        model = User

    @staticmethod
    def _modify_to_hashed_password(validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            validated_data["hashed_password"] = make_password(password)
        if "password_confirmation" in validated_data:
            del validated_data["password_confirmation"]

    @transaction.atomic
    def create(self, validated_data):
        self._modify_to_hashed_password(validated_data)
        validated_data["email_verification_token"] = Token.generate_key()
        user = super().create(validated_data)
        uri_path = reverse(
            "user-email-verification",
            kwargs={"pk": user.id},
            request=self.context["request"],
        )
        query = urlencode({"token": user.email_verification_token})
        send_mail(
            from_email="contact@konbinein.com",
            message=f"{uri_path}?{query}",
            recipient_list=[user.email],
            subject="Konbinein Email Verification",
        )
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        self._modify_to_hashed_password(validated_data)
        super().update(instance, validated_data)
        return instance

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirmation"):
            raise ValidationError(
                "Password doesn't match the confirmation.",
                "password_not_match_confirmation",
            )
        return attrs
