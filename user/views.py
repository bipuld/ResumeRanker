from django.shortcuts import render
from django.views import View

from utils.services import register_fcm_device

from user.serializers import PasswordResetConfirmSerializer

# Create your views here.


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
