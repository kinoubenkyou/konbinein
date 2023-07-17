from rest_framework.fields import BooleanField, ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer

from main.models.organization import Organization
from main.models.user import User


class StaffFilterSet(Serializer):
    does_organization_agree = BooleanField()
    does_user_agree = BooleanField()
    user__in = ListField(child=PrimaryKeyRelatedField(queryset=User.objects.all()))
    organization__in = ListField(
        child=PrimaryKeyRelatedField(queryset=Organization.objects.all())
    )
