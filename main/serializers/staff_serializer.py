from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from main.models.staff import Staff


class StaffSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "user",
            "user_email",
        )
        model = Staff
        read_only_fields = (
            "does_organization_agree",
            "does_user_agree",
        )

    user_email = CharField(read_only=True, source="user.email")

    def create(self, validated_data):
        staff_attributes = {
            **validated_data,
            "does_organization_agree": True,
            "does_user_agree": False,
            "organization_id": self.context["view"].kwargs["organization_id"],
        }
        return super().create(staff_attributes)

    def validate_user(self, value):
        if Staff.objects.filter(
            organization=self.context["view"].kwargs["organization_id"], user=value
        ).exists():
            raise ValidationError(detail="Staff is already created.")
        return value
