from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.product import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        fields = ("code", "name", "price")
        model = Product

    def create(self, validated_data):
        product_attributes = validated_data | {
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().create(product_attributes)

    def update(self, instance, validated_data):
        product_attributes = validated_data | {
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().update(instance, product_attributes)

    def validate_code(self, value):
        query_set = Product.objects.filter(
            code=value, organization=self.context["view"].kwargs["organization_id"]
        )
        if self.instance is not None:
            query_set = query_set.exclude(id=self.instance.id)
        if query_set.exists():
            raise ValidationError(detail="Code is already in another product.")
        return value
