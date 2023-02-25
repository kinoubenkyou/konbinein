from django.db.models import CharField, EmailField, Model


class User(Model):
    authentication_token = CharField(max_length=255, null=True, unique=True)
    email = EmailField(unique=True)
    email_verification_token = CharField(max_length=255, null=True)
    hashed_password = CharField(max_length=255)
    name = CharField(max_length=255, null=True)
