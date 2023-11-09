from secrets import token_urlsafe

from django.core.cache import cache


def get_email_verifying_token(user_id):
    return cache.get(f"email_verifying_token.{user_id}")


def get_password_resetting_token(user_id):
    return cache.get(f"password_resetting_token.{user_id}")


def set_email_verifying_token(user_id):
    cache.set(f"email_verifying_token.{user_id}", token_urlsafe())


def set_password_resetting_token(user_id):
    cache.set(f"password_resetting_token.{user_id}", token_urlsafe())
