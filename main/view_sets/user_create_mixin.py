from rest_framework.mixins import CreateModelMixin


class UserCreateMixin(CreateModelMixin):
    def perform_create(self, serializer):
        super().perform_create(serializer)
        request = self.request
        user = request.user
        self.activity_class(
            action=self.action,
            instance_id=serializer.instance.id,
            user_id=user.id,
            user_name=user.name,
            **request.data,
        ).save()
