from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class PersonnelSerializer(ModelSerializer):
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
        data["does_organization_agree"] = False
        data["does_user_agree"] = True
        data["user"] = self.context["request"].user.id
        return super().to_internal_value(data)
