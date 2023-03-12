from django.db import transaction
from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class OrganizationPersonnelSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "user",
        )
        model = Personnel
        read_only_fields = ("does_organization_agree", "does_user_agree")

    @transaction.atomic
    def create(self, validated_data):
        personnel_attributes = validated_data | {
            "does_organization_agree": True,
            "does_user_agree": False,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().create(personnel_attributes)
