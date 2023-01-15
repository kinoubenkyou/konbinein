from datetime import timezone

from django.contrib.auth.hashers import make_password
from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from main.models import Order, OrderItem, Organization, User


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = Sequence(lambda n: f"name{n}")


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = Sequence(lambda n: f"code{n}")
    created_at = Faker("past_datetime", tzinfo=timezone.utc)
    organization = SubFactory(OrganizationFactory)


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    name = Sequence(lambda n: f"name{n}")
    order = SubFactory(OrderFactory)
    quantity = Faker("pyint", max_value=100, min_value=1)
    unit_price = Faker("pydecimal", left_digits=2, positive=True, right_digits=2)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = Sequence(lambda n: f"email{n}@email.com")
    email_verification_token = None
    hashed_password = Sequence(lambda n: make_password(f"password{n}"))
    name = Sequence(lambda n: f"name{n}")
