from decimal import Decimal

from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.product import Product
from main.models.product_item import ProductItem


class ProductItemSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "name", "product", "quantity", "total", "price")
        model = ProductItem

    id = IntegerField(required=False)
    product = PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)

    def validate(self, data):
        if Decimal(data["total"]) != Decimal(data["price"]) * int(data["quantity"]):
            raise ValidationError(detail="Total is incorrect.")
        return data

    def validate_product(self, value):
        if value.organization_id != int(self.context["view"].kwargs["organization_id"]):
            raise ValidationError(detail="Product is in another organization.")
        return value
