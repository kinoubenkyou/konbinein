from django.db.models import CASCADE, BooleanField, ForeignKey, Model

from main.models.organization import Organization
from main.models.user import User


class Personnel(Model):
    class Meta:
        unique_together = (("organization", "user"),)

    does_organization_agree = BooleanField()
    does_user_agree = BooleanField()
    organization = ForeignKey(Organization, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
