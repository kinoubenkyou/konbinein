from rest_framework.serializers import ModelSerializer

from main.models.organization import Organization


class OrganizationSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "name")
        model = Organization
