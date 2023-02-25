from django.db import transaction
from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class OrganizationPersonnelSerializer(ModelSerializer):
    class Meta:
        fields = (
            "id",
            "does_organization_agree",
            "does_user_agree",
            "organization",
            "user",
        )
        model = Personnel
        read_only_fields = (
            "does_organization_agree",
            "does_user_agree",
            "organization",
        )

    @transaction.atomic
    def create(self, validated_data):
        organization_id = self.context["view"].kwargs["organization_id"]
        validated_data |= {
            "does_organization_agree": True,
            "does_user_agree": False,
            "organization_id": organization_id,
        }
        personnel = super().create(validated_data)
        return personnel
