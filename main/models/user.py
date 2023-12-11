from django.db.models import BooleanField, CharField, EmailField, Model


class User(Model):
    email = EmailField(unique=True)
    hashed_password = CharField(max_length=255)
    is_system_administrator = BooleanField()
    name = CharField(max_length=255, null=True)
