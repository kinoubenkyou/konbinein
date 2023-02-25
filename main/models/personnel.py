from django.db.models import CASCADE, BooleanField, ForeignKey, Model, UniqueConstraint

from main.models.organization import Organization
from main.models.user import User


class Personnel(Model):
    class Meta:
        constraints = (
            UniqueConstraint(
                "organization",
                "user",
                name="main_organizationuser_organization_id_user_id",
            ),
        )

    does_organization_agree = BooleanField()
    does_user_agree = BooleanField()
    organization = ForeignKey(Organization, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
