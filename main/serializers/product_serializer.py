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
