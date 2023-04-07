from django.db.models import CharField, Model


class Organization(Model):
    code = CharField(max_length=255, unique=True)
    name = CharField(max_length=255)
