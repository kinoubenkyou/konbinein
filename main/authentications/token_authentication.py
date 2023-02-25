from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from main.models.user import User


class TokenAuthentication(BaseAuthentication):
    SCHEME = "Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "").split()
        try:
            if header[0] != self.SCHEME:
                return None
        except IndexError:
            return None
        try:
            authorization_token = header[1]
        except IndexError:
            raise AuthenticationFailed()
        try:
            user = User.objects.get(authentication_token=authorization_token)
        except User.DoesNotExist:
            raise AuthenticationFailed()
        return user, None
