from rest_framework.viewsets import ModelViewSet

from main.models.organization import Organization
from main.serializers.organization_serializer import OrganizationSerializer


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
