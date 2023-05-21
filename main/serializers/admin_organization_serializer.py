from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from main.models.organization import Organization
from main.models.user import User


class AdminOrganizationSerializer(ModelSerializer):
    class Meta:
        fields = ("code", "id", "name", "user")
        model = Organization

    user = PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    def create(self, validated_data):
        user = validated_data.pop("user")
        organization = super().create(validated_data)
        organization.staff_set.create(
            does_organization_agree=True, does_user_agree=True, user=user
        )
        return organization
