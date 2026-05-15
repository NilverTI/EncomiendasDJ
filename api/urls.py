from django.urls import path
from rest_framework.routers import DefaultRouter

from api.viewsets import EncomiendaViewSet, ArticuloViewSet, OrdenViewSet
from api.views_v2 import ArticuloViewSetV2, OrdenViewSetV2
from api import api_views
from api import views as articulo_views

# v1 router
v1_router = DefaultRouter()
v1_router.register("encomiendas", EncomiendaViewSet, basename="encomienda")
v1_router.register("articulos", ArticuloViewSet, basename="articulo")
v1_router.register("ordenes", OrdenViewSet, basename="orden")

# v2 router
v2_router = DefaultRouter()
v2_router.register("encomiendas", EncomiendaViewSet, basename="encomienda")
v2_router.register("articulos", ArticuloViewSetV2, basename="articulo")
v2_router.register("ordenes", OrdenViewSetV2, basename="orden")

# Shared patterns included under both v1 and v2
shared_urlpatterns = [
    path(
        "fundamentos/fbv/encomiendas/",
        api_views.encomienda_fbv_list,
        name="encomienda-fbv-list",
    ),
    path(
        "fundamentos/fbv/encomiendas/<int:pk>/",
        api_views.encomienda_fbv_detail,
        name="encomienda-fbv-detail",
    ),
    path(
        "fundamentos/apiview/encomiendas/",
        api_views.EncomiendaListAPIView.as_view(),
        name="encomienda-apiview-list",
    ),
    path(
        "fundamentos/apiview/encomiendas/<int:pk>/",
        api_views.EncomiendaDetailAPIView.as_view(),
        name="encomienda-apiview-detail",
    ),
    path(
        "fundamentos/mixins/encomiendas/",
        api_views.EncomiendaMixinListCreateView.as_view(),
        name="encomienda-mixin-list",
    ),
    path(
        "fundamentos/mixins/encomiendas/<int:pk>/",
        api_views.EncomiendaMixinDetailView.as_view(),
        name="encomienda-mixin-detail",
    ),
    path(
        "fundamentos/generics/encomiendas/",
        api_views.EncomiendaGenericListCreateView.as_view(),
        name="encomienda-generic-list",
    ),
    path(
        "fundamentos/generics/encomiendas/<int:pk>/",
        api_views.EncomiendaGenericDetailView.as_view(),
        name="encomienda-generic-detail",
    ),
    path("clientes/", api_views.ClienteListView.as_view(), name="cliente-list"),
    path("rutas/", api_views.RutaListView.as_view(), name="ruta-list"),
]

# Demo articulo endpoints (not versioned)
articulo_demo_urlpatterns = [
    path("api/articulos/fbv/", articulo_views.articulo_list, name="articulo-fbv-list"),
    path("api/articulos/fbv/<int:pk>/", articulo_views.articulo_detail, name="articulo-fbv-detail"),
    path("api/articulos/apiview/", articulo_views.ArticuloListView.as_view(), name="articulo-apiview-list"),
    path("api/articulos/apiview/<int:pk>/", articulo_views.ArticuloDetailView.as_view(), name="articulo-apiview-detail"),
    path("api/articulos/mixins/", articulo_views.ArticuloListCreateGeneric.as_view(), name="articulo-mixin-list"),
    path("api/articulos/mixins/<int:pk>/", articulo_views.ArticuloDetailGeneric.as_view(), name="articulo-mixin-detail"),
    path("api/articulos/generics/", articulo_views.ArticuloListCreateSimple.as_view(), name="articulo-generic-list"),
    path("api/articulos/generics/<int:pk>/", articulo_views.ArticuloDetailSimple.as_view(), name="articulo-generic-detail"),
]
