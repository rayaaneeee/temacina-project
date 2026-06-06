from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/",    admin.site.urls),
    path("api/health/", include("health_check.urls")),
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
