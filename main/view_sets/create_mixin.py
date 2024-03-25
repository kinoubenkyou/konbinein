from rest_framework.mixins import CreateModelMixin

from main.shortcuts import OBSCURE_ACTIVITY_DATA_KEYS


class CreateMixin(CreateModelMixin):
    def perform_create(self, serializer):
        super().perform_create(serializer)
        request = self.request
        data = {
            key: value
            for key, value in request.data.items()
            if key not in OBSCURE_ACTIVITY_DATA_KEYS
        }
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
