from django.db import transaction
from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class PersonnelSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "organization",
        )
        model = Personnel
        read_only_fields = ("does_organization_agree", "does_user_agree")

    @transaction.atomic
    def create(self, validated_data):
        personnel_attributes = validated_data | {
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": self.context["request"].user.id,
        }
        return super().create(personnel_attributes)
