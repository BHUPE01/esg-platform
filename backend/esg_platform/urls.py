from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT Auth
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # App APIs (we'll wire these as we build each app)
    path("api/core/", include("apps.core.urls")),
    path("api/ingestion/", include("apps.ingestion.urls")),
    path("api/normalization/", include("apps.normalization.urls")),
    path("api/validation/", include("apps.validation.urls")),
    path("api/review/", include("apps.review.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)