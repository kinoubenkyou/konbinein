from rest_framework.serializers import ModelSerializer

from main.models.personnel import Personnel


class PersonnelSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Personnel
