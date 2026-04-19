from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path,include,re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from recruiter.api import AcceptInviteView
from user.views import PasswordResetConfirmTemplateView,resend_otp, verify_otp
urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'api/(?P<version>v1)/', include('user.urls')),
    re_path(r'api/(?P<version>v1)/', include('recruiter.urls')),
    path(
        "password/reset-confirm/",
        PasswordResetConfirmTemplateView.as_view(),
        name="password_reset_confirm_web",
    ),
    path("invite/<uuid:token>", AcceptInviteView.as_view(), name="invite-short"),
    path("invite/<uuid:token>/", AcceptInviteView.as_view(), name="invite-short-slash"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("resend-otp/", resend_otp, name="resend-otp"),
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
    path("ckeditor5/", include("django_ckeditor_5.urls")),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
