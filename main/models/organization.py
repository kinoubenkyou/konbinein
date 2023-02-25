from django.db.models import CharField, Model


class Organization(Model):
    name = CharField(max_length=255)
