from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from core.models import Articulo
from .viewsets import ArticuloViewSet, OrdenViewSet


class ArticuloViewSetV2(ArticuloViewSet):
    @action(detail=False, methods=["get"])
    def stats(self, request, **kwargs):
        data = (
            Articulo.objects
            .values("grupo__nombre")
            .annotate(total=Count("id"))
            .order_by("grupo__nombre")
        )
        return Response(list(data))


class OrdenViewSetV2(OrdenViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def pendientes(self, request, **kwargs):
        qs = self.get_queryset().filter(estado="PE")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
