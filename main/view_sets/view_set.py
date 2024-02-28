from rest_framework.viewsets import ModelViewSet

from main.view_sets.user_create_mixin import UserCreateMixin
from main.view_sets.user_destroy_mixin import UserDestroyMixin
from main.view_sets.user_update_mixin import UserUpdateMixin


class ViewSet(UserCreateMixin, UserDestroyMixin, UserUpdateMixin, ModelViewSet):
    pass
