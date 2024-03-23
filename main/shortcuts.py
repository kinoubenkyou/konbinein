from secrets import token_urlsafe

from django.core.cache import cache
from rest_framework.authtoken.models import Token

OBSCURE_ACTIVITY_DATA_KEYS = ("current_password", "password", "token")


class ActivityType:
    ADMIN = "admin"
    ORGANIZATION = "organization"
    PUBLIC = "public"
    USER = "user"
    ALL = (ADMIN, ORGANIZATION, PUBLIC, USER)


def delete_authentication_token(user_id):
    cache.delete(f"authentication_token.{user_id}")


def delete_email_verifying_token(user_id):
    cache.delete(f"email_verifying_token.{user_id}")


def delete_password_resetting_token(user_id):
    cache.delete(f"password_resetting_token.{user_id}")


def get_authentication_token(user_id):
    return cache.get(f"authentication_token.{user_id}")


def get_email_verifying_token(user_id):
    return cache.get(f"email_verifying_token.{user_id}")


def get_password_resetting_token(user_id):
    return cache.get(f"password_resetting_token.{user_id}")


def set_authentication_token(user_id):
    cache.set(f"authentication_token.{user_id}", Token.generate_key())


def set_email_verifying_token(user_id):
    cache.set(f"email_verifying_token.{user_id}", token_urlsafe())


def set_password_resetting_token(user_id):
    cache.set(f"password_resetting_token.{user_id}", token_urlsafe())
