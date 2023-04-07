from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.organization import Organization
from main.models.staff import Staff


class UserStaffSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "organization_code",
            "organization_id",
        )
        model = Staff
        read_only_fields = ("does_organization_agree", "does_user_agree")

    organization_code = CharField(read_only=True, source="organization.code")
    organization_id = PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source="organization"
    )

    def create(self, validated_data):
        staff_attributes = validated_data | {
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": self.context["view"].kwargs["user_id"],
        }
        return super().create(staff_attributes)

    def validate_organization_id(self, value):
        if Staff.objects.filter(
            organization=value, user=self.context["view"].kwargs["user_id"]
        ).exists():
            raise ValidationError(detail="Staff is already created.")
        return value
