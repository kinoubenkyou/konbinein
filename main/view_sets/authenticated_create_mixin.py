from rest_framework.mixins import CreateModelMixin


class AuthenticatedCreateMixin(CreateModelMixin):
    def perform_create(self, serializer):
        super().perform_create(serializer)
        request = self.request
        user = request.user
        self.activity_class(
            action=self.action,
            data=request.data,
            object_id=serializer.instance.id,
            user_id=getattr(user, "id", None),
            user_name=getattr(user, "name", None),
        ).save()
