from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    """Friendly landing page so '/' doesn't look like an error."""
    return JsonResponse(
        {
            "status": "ok",
            "message": "Speaking backend ishlayapti.",
            "endpoints": {
                "admin": "/admin/",
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "me": "/api/auth/me/",
                "questions": "/api/questions/",
                "results": "/api/results/",
            },
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/questions/", include("questions.urls")),
    path("api/results/", include("results.urls")),
]
