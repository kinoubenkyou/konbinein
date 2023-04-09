from rest_framework.fields import BooleanField, ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer

from main.models.organization import Organization


class UserStaffFilterSet(Serializer):
    does_organization_agree = BooleanField()
    does_user_agree = BooleanField()
    organization_id__in = ListField(
        child=PrimaryKeyRelatedField(queryset=Organization.objects.all())
    )