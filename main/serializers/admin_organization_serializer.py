from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.organization import Organization
from main.models.user import User


class AdminOrganizationSerializer(ModelSerializer):
    class Meta:
        fields = ("code", "id", "name", "user_id")
        model = Organization

    user_id = PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        organization = super().create(validated_data)
        organization.staff_set.create(
            does_organization_agree=True, does_user_agree=True, user=user_id
        )
        return organization
