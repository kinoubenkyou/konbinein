from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.organization import Organization
from main.models.user import User


class AdminOrganizationSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        fields = ("id", "name", "user")
        model = Organization

    def create(self, validated_data):
        user_id = validated_data.pop("user")
        organization = super().create(validated_data)
        organization.personnel_set.create(
            does_organization_agree=True, does_user_agree=True, user=user_id
        )
        return organization
