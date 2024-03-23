from rest_framework.mixins import CreateModelMixin


class CreateMixin(CreateModelMixin):
    def perform_create(self, serializer):
        super().perform_create(serializer)
        request = self.request
        instance = serializer.instance
        self.activity_class.objects.create(
            creator_id=getattr(request.user, "id", None),
            creator_organization_id=self.kwargs.get("organization_id"),
            creator_type=self.activity_type,
            data=request.data,
            object_id=instance.id,
            organization_id=getattr(instance, "organization_id", None),
            user_id=getattr(instance, "user_id", None),
        )
