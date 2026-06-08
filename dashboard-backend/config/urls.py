from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path("admin/",    admin.site.urls),
    
    # Health check
    path("api/health/", include("health_check.urls")),
    
    # API Documentation (Swagger/ReDoc)
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # API Routes
    path("api/v1/auth/",          include("apps.authentication.api.urls")),
    path("api/v1/users/",         include("apps.users.api.urls")),
    path("api/v1/analytics/",     include("apps.analytics.api.urls")),
    path("api/v1/reports/",       include("apps.reports.api.urls")),
    path("api/v1/notifications/", include("apps.notifications.api.urls")),
    path("api/v1/", include("apps.safex.api.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
