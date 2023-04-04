from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from main.models.staff import Staff


class OrganizationStaffSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "organization",
            "user",
        )
        model = Staff
        read_only_fields = (
            "does_organization_agree",
            "does_user_agree",
            "organization",
        )

    def create(self, validated_data):
        staff_attributes = validated_data | {
            "does_organization_agree": True,
            "does_user_agree": False,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().create(staff_attributes)

    def validate_user(self, value):
        if Staff.objects.filter(
            user=value, organization=self.context["view"].kwargs["organization_id"]
        ).exists():
            raise ValidationError(detail="Staff is already created.")
        return value
