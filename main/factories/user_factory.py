from random import choice
from string import ascii_uppercase

from django.contrib.auth.hashers import make_password
from factory import LazyAttribute, Sequence
from factory.django import DjangoModelFactory

from main.models.user import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = Sequence(lambda n: f"email-{choice(ascii_uppercase)}{n}@email.com")
    hashed_password = LazyAttribute(lambda user: make_password(user.password))
    is_system_administrator = False
    name = Sequence(lambda n: f"name-{choice(ascii_uppercase)}{n}")
    password = Sequence(lambda n: f"password-{choice(ascii_uppercase)}{n}")

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password")
        user = super()._build(model_class, *args, **kwargs)
        user.password = password
        return user

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password")
        user = super()._create(model_class, *args, **kwargs)
        user.password = password
        return user
