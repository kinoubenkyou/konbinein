from rest_framework.viewsets import ModelViewSet

from main.view_sets.authenticated_create_mixin import AuthenticatedCreateMixin
from main.view_sets.authenticated_update_mixin import AuthenticatedUpdateMixin


class AuthenticatedViewSet(
    AuthenticatedCreateMixin,
    AuthenticatedUpdateMixin,
    ModelViewSet,
):
    pass
