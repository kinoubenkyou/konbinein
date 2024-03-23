from rest_framework.mixins import UpdateModelMixin


class UpdateMixin(UpdateModelMixin):
    def perform_update(self, serializer):
        request = self.request
        initial_instance_data = self.get_serializer_class()(serializer.instance).data
        data = {
            key: value
            for key, value in request.data.items()
            if value != str(initial_instance_data.get(key))
        }
        super().perform_update(serializer)
        instance = serializer.instance
        self.activity_class.objects.create(
            creator_id=getattr(request.user, "id", None),
            creator_organization_id=self.kwargs.get("organization_id"),
            creator_type=self.activity_type,
            data=data,
            object_id=instance.id,
            organization_id=getattr(instance, "organization_id", None),
            user_id=getattr(instance, "user_id", None),
        )
