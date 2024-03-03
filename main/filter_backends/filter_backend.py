from rest_framework.filters import BaseFilterBackend


class FilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_set_class = getattr(view, "filter_set_class", None)
        if filter_set_class is not None:
            filter_set = filter_set_class(data=request.query_params, partial=True)
            filter_set.is_valid(raise_exception=True)
            return queryset.filter(**filter_set.validated_data).distinct()
        else:
            return queryset
