from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.views import View

from utils.services import register_fcm_device

from user.serializers import PasswordResetConfirmSerializer, VerifyOTPSerializer, ResendOTPSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.utils import generate_otp, send_otp
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

# Create your views here.
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordResetConfirmTemplateView(View):
    template_name = "user/password_reset_confirm.html"

    def get(self, request, *args, **kwargs):
        print(request.GET)
        uid = request.GET.get("u")
        token = request.GET.get("t")
        return render(request, self.template_name, {"uid": uid, "token": token})

    def post(self, request):
        data = {
            "uid": request.POST.get("uid"),
            "token": request.POST.get("token"),
            "new_password": request.POST.get("new_password"),
            "confirm_password": request.POST.get("confirm_password"),
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return render(
                request,
                self.template_name,
                {"success": "Password has been successfully reset!"},
            )
        else:
            error_field = next(iter(serializer.errors.keys()))
            error_message = serializer.errors[error_field][0]
            return render(
                request,
                self.template_name,
                {
                    "uid": data["uid"],
                    "token": data["token"],
                    "error": error_message,
                },
            )
from drf_spectacular.utils import extend_schema
@extend_schema(
    request=VerifyOTPSerializer,
    responses={200: dict}
)
@api_view(["POST"])
def verify_otp(request,*args, **kwargs):
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response(serializer.save())

@extend_schema(
    request=ResendOTPSerializer,
    responses={200: dict}
)

@api_view(["POST"])
def resend_otp(request,*args, **kwargs):
    serializer = ResendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response(serializer.save())