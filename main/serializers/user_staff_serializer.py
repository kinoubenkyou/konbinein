from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.staff import Staff


class UserStaffSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "organization",
            "organization_code",
        )
        model = Staff
        read_only_fields = ("does_organization_agree", "does_user_agree")

    organization_code = CharField(read_only=True, source="organization.code")

    def create(self, validated_data):
        staff_attributes = {
            **validated_data,
            "does_organization_agree": False,
            "does_user_agree": True,
            "user_id": self.context["view"].kwargs["user_id"],
        }
        return super().create(staff_attributes)

    def validate_organization(self, value):
        if Staff.objects.filter(
            organization=value, user=self.context["view"].kwargs["user_id"]
        ).exists():
            raise ValidationError(detail="Staff is already created.")
        return value
