from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from api.urls import v1_router, v2_router, shared_urlpatterns, articulo_demo_urlpatterns
from api.auth import EncomiendaTokenView

admin.site.site_header = "Sistema de Gesti\xf3n de Encomiendas"
admin.site.site_title = "Encomiendas Admin"
admin.site.index_title = "Panel de Administraci\xf3n"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("envios.urls")),
    # Versioned API
    path("api/v1/", include(v1_router.urls + shared_urlpatterns), {"version": "v1"}),
    path("api/v2/", include(v2_router.urls + shared_urlpatterns), {"version": "v2"}),
    # Standalone JWT
    path("api/token/", EncomiendaTokenView.as_view(), name="token_obtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Demo articulo endpoints (not versioned)
    *articulo_demo_urlpatterns,
    # Schema and docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        from silk import urls as silk_urls
        urlpatterns += [
            path("silk/", include(silk_urls.urls, namespace="silk")),
        ]
    except ImportError:
        pass
