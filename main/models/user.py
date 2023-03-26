from django.db.models import BooleanField, CharField, EmailField, Model


class User(Model):
    authentication_token = CharField(max_length=255, null=True, unique=True)
    email = EmailField(unique=True)
    email_verifying_token = CharField(max_length=255, null=True)
    hashed_password = CharField(max_length=255)
    is_system_administrator = BooleanField()
    name = CharField(max_length=255, null=True)
