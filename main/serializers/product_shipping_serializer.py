from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.product_shipping import ProductShipping


class ProductShippingSerializer(ModelSerializer):
    class Meta:
        fields = ("code", "fixed_fee", "id", "name", "products", "unit_fee", "zones")
        model = ProductShipping

    def create(self, validated_data):
        product_shipping_attributes = {
            **validated_data,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().create(product_shipping_attributes)

    def update(self, instance, validated_data):
        product_shipping_attributes = {
            **validated_data,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().update(instance, product_shipping_attributes)

    def validate_code(self, value):
        query_set = ProductShipping.objects.filter(
            code=value, organization=self.context["view"].kwargs["organization_id"]
        )
        if self.instance is not None:
            query_set = query_set.exclude(id=self.instance.id)
        if query_set.exists():
            raise ValidationError(detail="Code is already in another product shipping.")
        return value

    def validate_products(self, values):
        if any(
            product.organization_id
            != int(self.context["view"].kwargs["organization_id"])
            for product in values
        ):
            raise ValidationError(detail="Products are in another organization.")
        return values
