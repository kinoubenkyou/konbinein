from django.contrib.postgres.fields import ArrayField
from django.db.models import CASCADE, CharField, DecimalField, ForeignKey, Model

from main.models import ZONE_CHOICES
from main.models.organization import Organization


class Shipping(Model):
    class Meta:
        abstract = True

    code = CharField(max_length=255)
    fixed_fee = DecimalField(decimal_places=4, max_digits=19)
    name = CharField(max_length=255)
    organization = ForeignKey(Organization, on_delete=CASCADE)
    unit_fee = DecimalField(decimal_places=4, max_digits=19)
    zones = ArrayField(CharField(max_length=255, choices=ZONE_CHOICES))
