from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from main.models.user import User
from main.shortcuts import get_authentication_token


class BearerAuthentication(BaseAuthentication):
    SCHEME = "Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "").split()
        try:
            if header[0] != self.SCHEME:
                return None
        except IndexError:
            return None
        try:
            user_id = header[1]
            token = header[2]
            if get_authentication_token(user_id) != token:
                raise AuthenticationFailed()
            user = User.objects.get(id=user_id)
        except IndexError:
            raise AuthenticationFailed()
        return user, None
