from django.urls import include, path, re_path

from user.api import (
    TokenRefreshView,
    UserLoginAPI,
    LogoutAPIView,
    PasswordChangeAPI,
    PasswordResetAPI,
    UserSignUpAPI,
)
from user.views import PasswordResetConfirmTemplateView, resend_otp

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh-api"),
    path(
        "user/",
        include(
            [
                path("signup/", UserSignUpAPI.as_view(), name="signup-api"),
                path("login/", UserLoginAPI.as_view(), name="login-api"),
                path("logout/", LogoutAPIView.as_view()),
                path(
                    "password/change/",
                    PasswordChangeAPI.as_view(),
                    name="password-change-api",
                ),
                path("reset/", PasswordResetAPI.as_view(), name="password_reset_api"),
                path("resend-otp/", resend_otp, name="resend-otp"),
            ]
        ),
    ),
]
