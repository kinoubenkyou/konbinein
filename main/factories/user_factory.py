from django.contrib.auth.hashers import make_password
from factory import Sequence
from factory.django import DjangoModelFactory

from main.models.user import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = Sequence(lambda n: f"email{n}@email.com")
    email_verification_token = None
    hashed_password = Sequence(lambda n: make_password(f"password{n}"))
    name = Sequence(lambda n: f"name{n}")
