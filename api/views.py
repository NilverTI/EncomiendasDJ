from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.views import APIView
from core.models import Articulo, OrdenCompraCliente
from api.serializers import ArticuloSerializer, ArticuloListSerializer


@api_view(["GET", "POST"])
def articulo_list(request):
    if request.method == "GET":
        articulos = Articulo.objects.all()
        serializer = ArticuloListSerializer(articulos, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ArticuloSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def articulo_detail(request, pk):
    try:
        articulo = Articulo.objects.get(pk=pk)
    except Articulo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ArticuloSerializer(articulo)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ArticuloSerializer(articulo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        articulo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def articulo_create(request):
    serializer = ArticuloSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticuloListView(APIView):
    def get(self, request):
        articulos = Articulo.objects.all()
        serializer = ArticuloListSerializer(articulos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticuloSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticuloDetailView(APIView):
    def get_object(self, pk):
        try:
            return Articulo.objects.get(pk=pk)
        except Articulo.DoesNotExist:
            return None

    def get(self, request, pk):
        articulo = self.get_object(pk)
        if not articulo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ArticuloSerializer(articulo)
        return Response(serializer.data)

    def put(self, request, pk):
        articulo = self.get_object(pk)
        if not articulo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ArticuloSerializer(articulo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        articulo = self.get_object(pk)
        if not articulo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        articulo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticuloListCreateGeneric(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                generics.GenericAPIView):
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ArticuloDetailGeneric(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            generics.GenericAPIView):
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ArticuloListCreateSimple(generics.ListCreateAPIView):
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer


class ArticuloDetailSimple(generics.RetrieveUpdateDestroyAPIView):
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer
