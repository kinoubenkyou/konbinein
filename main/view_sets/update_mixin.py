from rest_framework.mixins import UpdateModelMixin

from main.shortcuts import OBSCURE_ACTIVITY_DATA_KEYS


class UpdateMixin(UpdateModelMixin):
    def perform_update(self, serializer):
        super().perform_update(serializer)
        instance = serializer.instance
        request = self.request
        lastest_activity_data = getattr(
            self.activity_class.objects.filter(object_id=instance.id)
            .order_by("-id")
            .first(),
            "data",
            {},
        )
        data = {
            key: value
            for key, value in request.data.items()
            if key not in OBSCURE_ACTIVITY_DATA_KEYS
            and (
                key not in lastest_activity_data or value != lastest_activity_data[key]
            )
        }
        self.activity_class.objects.create(
            creator_id=getattr(request.user, "id", None),
            creator_organization_id=self.kwargs.get("organization_id"),
            creator_type=self.activity_type,
            data=data,
            object_id=instance.id,
            organization_id=getattr(instance, "organization_id", None),
            user_id=getattr(instance, "user_id", None),
        )
