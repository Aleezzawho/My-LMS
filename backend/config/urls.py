from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from config.api import api

handler404 = "config.urls.not_found"
handler500 = "config.urls.server_error"


def not_found(request, exception=None):
    if request.path.startswith("/api/"):
        return JsonResponse(
            {
                "code": "not_found",
                "message": "Resource not found.",
                "details": None,
                "request_id": getattr(request, "request_id", ""),
            },
            status=404,
        )
    return JsonResponse({"code": "not_found", "message": "Resource not found."}, status=404)


def server_error(request):
    return JsonResponse(
        {"code": "internal_error", "message": "Something went wrong."}, status=500
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
