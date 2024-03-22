from django.db.models import QuerySet
from rest_framework.filters import BaseFilterBackend


class FilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_set_class = getattr(view, "filter_set_class", None)
        if filter_set_class is not None:
            filter_set = filter_set_class(data=request.query_params, partial=True)
            filter_set.is_valid(raise_exception=True)
            query_set = queryset.filter(**filter_set.validated_data)
            if isinstance(queryset, QuerySet):
                query_set = query_set.distinct()
            return query_set
        return queryset
