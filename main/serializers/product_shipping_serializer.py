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
        product_data_list = product_shipping_attributes.pop("products", ())
        product_shipping = super().create(product_shipping_attributes)
        product_shipping.products.set(
            product_data.id for product_data in product_data_list
        )
        return product_shipping

    def update(self, instance, validated_data):
        product_shipping_attributes = {
            **validated_data,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().update(instance, product_shipping_attributes)

    def validate(self, data):
        query_set = ProductShipping.objects.filter(
            organization=self.context["view"].kwargs["organization_id"],
            products__in=data["products"],
            zones__overlap=data["zones"],
        )
        if self.instance is not None:
            query_set = query_set.exclude(id=self.instance.id)
        if query_set.exists():
            raise ValidationError(detail="Products already have shipping with zones.")
        return data

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
