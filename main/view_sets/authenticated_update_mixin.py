from rest_framework.mixins import UpdateModelMixin


class AuthenticatedUpdateMixin(UpdateModelMixin):
    def perform_update(self, serializer):
        request = self.request
        initial_instance_data = self.serializer_class(serializer.instance).data
        data = {
            key: value
            for key, value in request.data.items()
            if value != str(initial_instance_data.get(key))
        }
        super().perform_update(serializer)
        user = request.user
        self.activity_class(
            action=self.action,
            instance_id=serializer.instance.id,
            user_id=user.id,
            user_name=user.name,
            **data,
        ).save()
