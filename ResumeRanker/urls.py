from django.contrib import admin
from django.urls import path,include,re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from user.views import PasswordResetConfirmTemplateView
urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'api/(?P<version>v1)/', include('user.urls')),
    path(
        "password/reset-confirm/",
        PasswordResetConfirmTemplateView.as_view(),
        name="password_reset_confirm_web",
    ),
    path(
        "api/",
        include([
            path("", SpectacularAPIView.as_view(), name="schema"),
            path(
                "swagger/",
                SpectacularSwaggerView.as_view(url_name="schema"),
                name="swagger-ui",
            ),
            path(
                "redoc/",
                SpectacularRedocView.as_view(url_name="schema"),
                name="redoc",
            ),
        ]),
    ),
]
