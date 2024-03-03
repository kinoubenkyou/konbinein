from rest_framework.mixins import DestroyModelMixin


class AuthenticatedDestroyMixin(DestroyModelMixin):
    def perform_destroy(self, instance):
        object_id = instance.id
        super().perform_destroy(instance)
        request = self.request
        user = request.user
        self.activity_class(
            action=self.action,
            object_id=object_id,
            user_id=user.id,
            user_name=user.name,
            **request.data,
        ).save()
