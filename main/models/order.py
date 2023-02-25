from django.db.models import CASCADE, CharField, DateTimeField, ForeignKey, Model

from main.models.organization import Organization


class Order(Model):
    code = CharField(max_length=255, unique=True)
    created_at = DateTimeField()
    organization = ForeignKey(Organization, on_delete=CASCADE)
