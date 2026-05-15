from collections import OrderedDict

from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination,
)
from rest_framework.response import Response


class EncomiendaPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "example": 120},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": schema,
            },
        }


class ClientePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class HistorialPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50


class EncomiendaCursorPagination(CursorPagination):
    page_size = 15
    ordering = "-fecha_registro"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ("links", OrderedDict([
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
            ])),
            ("count", self.page.paginator.count),
            ("pages", self.page.paginator.num_pages),
            ("current_page", self.page.number),
            ("results", data),
        ]))
