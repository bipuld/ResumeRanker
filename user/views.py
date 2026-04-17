from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.views import View

from utils.services import register_fcm_device

from user.serializers import PasswordResetConfirmSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.utils import generate_otp, send_otp
from rest_framework_simplejwt.tokens import RefreshToken
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




@api_view(["POST"])
def verify_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not user.otp or not user.otp_created_at:
        return Response({"error": "OTP not generated"}, status=400)

    if timezone.now() > user.otp_created_at + timedelta(minutes=1):
        return Response({"error": "OTP expired. Please request a new OTP."}, status=400)

    # then check OTP
    if user.otp != otp:
        return Response({"error": "Invalid OTP"}, status=400)

    user.is_verified = True
    user.otp = None
    user.is_email_verified = True
    user.otp_created_at = None
    user.save()


    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Account verified successfully",
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "id": str(user.id),
            "email": user.email,
        }
    })


@api_view(["POST"])
def resend_otp(request,*args, **kwargs):
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if user.is_verified:
        return Response({"message": "User already verified"})
    now = timezone.now()

    if user.otp_last_sent and now > user.otp_last_sent + timedelta(minutes=10):
        user.otp_attempts = 0
    if user.otp_last_sent and now < user.otp_last_sent + timedelta(seconds=30):
        return Response(
            {"error": "Please wait 30 seconds before requesting again"},
            status=429
        )

    if user.otp_attempts >= 3:
        return Response(
            {"error": "Too many requests. Try again after 10 minutes"},
            status=429
        )

    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = now

    # ✅ Update tracking (ALWAYS)
    user.otp_last_sent = now
    user.otp_attempts += 1

    user.save()
    send_otp(user)

    return Response({"message": "New OTP sent"})