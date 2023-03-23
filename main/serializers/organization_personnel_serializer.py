from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class OrganizationPersonnelSerializer(ModelSerializer):
    class Meta:
        fields = (
            "does_organization_agree",
            "does_user_agree",
            "id",
            "organization",
            "user",
        )
        model = Personnel

    def to_internal_value(self, data):
        data["does_organization_agree"] = True
        data["does_user_agree"] = False
        data["organization"] = self.context["view"].kwargs["organization_id"]
        return super().to_internal_value(data)
