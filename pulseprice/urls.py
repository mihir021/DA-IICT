from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve


urlpatterns = [
    path("api/", include("apps.health.urls")),
    path("api/", include("apps.admin_api.urls")),
    path("", include("apnaCart.urls")),
    re_path(
        r"^frontend/(?P<path>.*)$",
        serve,
        {"document_root": settings.BASE_DIR / "frontend"},
    ),
]
