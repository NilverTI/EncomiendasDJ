from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.viewsets import EncomiendaViewSet
from api import api_views
from api.auth import EncomiendaTokenView

router = DefaultRouter()
router.register("encomiendas", EncomiendaViewSet, basename="encomienda")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", EncomiendaTokenView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-redoc",
    ),
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
