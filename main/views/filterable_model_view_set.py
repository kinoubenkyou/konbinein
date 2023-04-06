from rest_framework.viewsets import GenericViewSet, ModelViewSet


class FilterableGenericViewSet(GenericViewSet):
    filter_set_class = None

    def filter_queryset(self, queryset):
        filter_set_class = self.get_filter_set_class()
        filter_set = filter_set_class(data=self.request.query_params, partial=True)
        filter_set.is_valid(raise_exception=True)
        filtered_query_set = queryset.filter(**filter_set.validated_data)
        return super().filter_queryset(filtered_query_set)

    def get_filter_set_class(self):
        assert self.filter_set_class is not None
        return self.filter_set_class


class FilterableModelViewSet(FilterableGenericViewSet, ModelViewSet):
    pass
