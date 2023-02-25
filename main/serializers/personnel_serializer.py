from django.db import transaction
from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class PersonnelSerializer(ModelSerializer):
    class Meta:
        fields = (
            "id",
            "does_organization_agree",
            "does_user_agree",
            "organization",
            "user",
        )
        model = Personnel
        read_only_fields = ("does_organization_agree", "does_user_agree", "user")

    @transaction.atomic
    def create(self, validated_data):
        user_id = self.context["request"].user.id
        validated_data |= {
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": user_id,
        }
        personnel = super().create(validated_data)
        return personnel
