from rest_framework.mixins import UpdateModelMixin


class AuthenticatedUpdateMixin(UpdateModelMixin):
    def perform_update(self, serializer):
        request = self.request
        initial_instance_data = self.get_serializer_class()(serializer.instance).data
        data = {
            key: value
            for key, value in request.data.items()
            if value != str(initial_instance_data.get(key))
        }
        super().perform_update(serializer)
        user = request.user
        self.activity_class(
            action=self.action,
            data=data,
            object_id=serializer.instance.id,
            user_id=getattr(user, "id", None),
            user_name=getattr(user, "name", None),
        ).save()
