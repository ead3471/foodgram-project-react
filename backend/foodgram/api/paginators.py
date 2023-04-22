from rest_framework.pagination import PageNumberPagination


class PageLimitedPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
