from django.urls import include, path


urlpatterns = [
    path("api/", include("apps.health.urls")),
    path("api/", include("apps.admin_api.urls")),
]
