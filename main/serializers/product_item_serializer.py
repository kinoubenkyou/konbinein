from rest_framework.fields import DecimalField, IntegerField
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
    total = DecimalField(decimal_places=4, max_digits=19, read_only=True)