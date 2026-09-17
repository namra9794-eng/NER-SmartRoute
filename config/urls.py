"""
Root URL configuration.

Final API surface (mirrors the platform's functional spec a-h):

  /api/auth/...                 -> JWT login/refresh, registration, profile
  /api/roads/                   -> GET/POST/PATCH road & district accessibility
  /api/incidents/               -> field-reported, geo-tagged incidents (photos)
  /api/vehicles/                -> GPS-tracked vehicles carrying essential cargo
  /api/vehicles/{id}/ping/      -> live GPS location update
  /api/logistics/shipments/     -> shipment / consignment tracking
  /api/routes/optimize/         -> AI/risk-aware alternate route suggestion
  /api/weather/                 -> weather records + sync-from-API
  /api/predictions/risk/        -> ML risk scoring endpoint
  /api/alerts/                  -> auto-generated + manual alerts, multilingual
  /api/dashboard/...            -> aggregated dashboard views
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("users.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/", include("roads.urls")),
    path("api/", include("incidents.urls")),
    path("api/", include("vehicles.urls")),
    path("api/", include("logistics.urls")),
    path("api/", include("routes.urls")),
    path("api/", include("weather.urls")),
    path("api/", include("alerts.urls")),
    path("api/", include("ml_engine.urls")),
    path("api/dashboard/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
