from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from envios.models import Encomienda, Empleado
from clientes.models import Cliente
from rutas.models import Ruta

from api.serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    ClienteSerializer,
    RutaSerializer,
)
from api.pagination import ClientePagination
from api.permissions import EsEmpleadoActivo, EsPropietarioOAdmin


def _empleado_de_usuario(user):
    empleado = getattr(user, "empleado", None)
    if empleado is not None:
        return empleado
    return Empleado.objects.get(email=user.email)


@extend_schema(
    methods=["GET"],
    responses=EncomiendaSerializer(many=True),
    tags=["DRF Fundamentos"],
)
@extend_schema(
    methods=["POST"],
    request=EncomiendaSerializer,
    responses={201: EncomiendaSerializer},
    tags=["DRF Fundamentos"],
)
@api_view(["GET", "POST"])
@permission_classes([EsEmpleadoActivo])
def encomienda_fbv_list(request, version=None):
    if request.method == "GET":
        qs = Encomienda.objects.con_relaciones()
        serializer = EncomiendaSerializer(
            qs, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = EncomiendaSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save(empleado_registro=_empleado_de_usuario(request.user))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=["GET"],
    responses=EncomiendaDetailSerializer,
    tags=["DRF Fundamentos"],
)
@extend_schema(
    methods=["PUT"],
    request=EncomiendaSerializer,
    responses=EncomiendaSerializer,
    tags=["DRF Fundamentos"],
)
@extend_schema(
    methods=["PATCH"],
    request=EncomiendaSerializer,
    responses=EncomiendaSerializer,
    tags=["DRF Fundamentos"],
)
@extend_schema(
    methods=["DELETE"],
    responses={204: None},
    tags=["DRF Fundamentos"],
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([EsEmpleadoActivo])
def encomienda_fbv_detail(request, pk, version=None):
    enc = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)

    if request.method == "GET":
        serializer = EncomiendaDetailSerializer(enc, context={"request": request})
        return Response(serializer.data)

    if request.method in ["PUT", "PATCH"]:
        serializer = EncomiendaSerializer(
            enc,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    enc.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class EncomiendaListAPIView(APIView):
    serializer_class = EncomiendaSerializer
    permission_classes = [EsEmpleadoActivo]

    @extend_schema(
        responses=EncomiendaSerializer(many=True),
        tags=["DRF Fundamentos"],
    )
    def get(self, request, version=None):
        qs = Encomienda.objects.con_relaciones()
        serializer = EncomiendaSerializer(
            qs, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        request=EncomiendaSerializer,
        responses={201: EncomiendaSerializer},
        tags=["DRF Fundamentos"],
    )
    def post(self, request, version=None):
        serializer = EncomiendaSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(empleado_registro=_empleado_de_usuario(request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EncomiendaDetailAPIView(APIView):
    serializer_class = EncomiendaSerializer
    permission_classes = [EsEmpleadoActivo]

    def get_object(self, pk):
        return get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)

    @extend_schema(
        responses=EncomiendaDetailSerializer,
        tags=["DRF Fundamentos"],
    )
    def get(self, request, pk, version=None):
        enc = self.get_object(pk)
        serializer = EncomiendaDetailSerializer(enc, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        request=EncomiendaSerializer,
        responses=EncomiendaSerializer,
        tags=["DRF Fundamentos"],
    )
    def put(self, request, pk, version=None):
        enc = self.get_object(pk)
        serializer = EncomiendaSerializer(
            enc, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=EncomiendaSerializer,
        responses=EncomiendaSerializer,
        tags=["DRF Fundamentos"],
    )
    def patch(self, request, pk, version=None):
        enc = self.get_object(pk)
        serializer = EncomiendaSerializer(
            enc, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        tags=["DRF Fundamentos"],
    )
    def delete(self, request, pk, version=None):
        enc = self.get_object(pk)
        enc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EncomiendaMixinListCreateView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    serializer_class = EncomiendaSerializer
    permission_classes = [EsEmpleadoActivo]

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(empleado_registro=_empleado_de_usuario(self.request.user))


class EncomiendaMixinDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = EncomiendaSerializer
    permission_classes = [EsEmpleadoActivo, EsPropietarioOAdmin]

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EncomiendaGenericListCreateView(generics.ListCreateAPIView):
    serializer_class = EncomiendaSerializer
    permission_classes = [EsEmpleadoActivo]

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def perform_create(self, serializer):
        serializer.save(empleado_registro=_empleado_de_usuario(self.request.user))


class EncomiendaGenericDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [EsEmpleadoActivo, EsPropietarioOAdmin]

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return EncomiendaDetailSerializer
        return EncomiendaSerializer


@extend_schema(
    summary="Listar clientes activos",
    description="Devuelve todos los clientes con estado Activo, paginados de 20 en 20.",
    tags=["Clientes"],
)
class ClienteListView(generics.ListAPIView):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination

    def get_queryset(self):
        return Cliente.objects.activos()


@extend_schema(
    summary="Listar rutas activas",
    description="Devuelve todas las rutas con estado Activo. Sin paginacion.",
    tags=["Rutas"],
)
class RutaListView(generics.ListAPIView):
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Ruta.objects.activas()
