from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


def apply_search(queryset, search_term, fields):
    if not search_term:
        return queryset
    query = Q()
    for field in fields:
        query |= Q(**{f"{field}__icontains": search_term})
    return queryset.filter(query)


def apply_sort(queryset, sort_param, allowed_fields, default='-created_at'):
    if not sort_param:
        return queryset.order_by(default)
    field = sort_param.lstrip('-')
    if field not in allowed_fields:
        return queryset.order_by(default)
    direction = '-' if sort_param.startswith('-') else ''
    return queryset.order_by(f"{direction}{field}")
