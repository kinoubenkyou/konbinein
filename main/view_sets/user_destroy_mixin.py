from rest_framework.mixins import DestroyModelMixin


class UserDestroyMixin(DestroyModelMixin):
    def perform_destroy(self, instance):
        instance_id = instance.id
        super().perform_destroy(instance)
        request = self.request
        user = request.user
        self.activity_class(
            action=self.action,
            instance_id=instance_id,
            user_id=user.id,
            user_name=user.name,
            **request.data,
        ).save()
