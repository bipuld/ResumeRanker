import os
from datetime import datetime

from fcm_django.models import FCMDevice
from rest_framework.exceptions import ValidationError


# def profile_image_upload_to(instance, filename):
#     """
#     Return upload path for user profile image:
#     media/profile_images/YYYY-MM-DD/username/profile.<ext>

#     If username is missing, use user UUID instead.
#     File is always renamed to 'profile.<extension>'.
#     """
#     # Extract file extension (lowercase)
#     ext = filename.split(".")[-1].lower()

#     # New filename fixed as 'profile.<ext>'
#     new_filename = f"profile.{ext}"

#     # Get current date string, e.g. '2025-07-11'
#     today = datetime.today().strftime("%Y-%m-%d")

#     # Get username or fallback to user id as string
#     username = getattr(instance.user, "username", None) or str(instance.user.id)

#     # Build the full path
#     # This results in: profile_images/2025-07-11/username/profile.jpg
#     return os.path.join("profile_images", today, username, new_filename)


# def school_document_upload_path(instance, filename: str) -> str:
#     """Generate upload path for school registration documents."""
#     return f"school/documents/{instance.id}/{filename}"


# def school_logo_upload_path(instance, filename: str) -> str:
#     """Generate upload path for school logos."""
#     return f"school/logos/{instance.id}/{filename}"


# def school_thumbnail_upload_path(instance, filename: str) -> str:
#     """Generate upload path for school thumbnail images."""
#     return f"school/thumbnails/{instance.id}/{filename}"


def register_fcm_device(user, request):
    """
    Register or update an FCM device for the given user.
    Handles unique registration_id constraint.
    """
    fcm_token = request.data.get("fcm_token")
    device_type = request.data.get("device_type", "web").lower()
    device_name = request.data.get("device_name", f"{device_type.title()} Device")
    device_id = request.data.get("device_id")

    if not fcm_token:
        return

    try:
        device, created = FCMDevice.objects.get_or_create(
            registration_id=fcm_token,
            defaults={
                "user": user,
                "type": device_type,
                "name": device_name,
                "device_id": device_id,
                "active": True,
            },
        )
        if not created:
            device.user = user
            device.type = device_type
            device.name = device_name
            device.device_id = device_id
            device.active = True
            device.save()
    except Exception as e:
        raise ValidationError({"fcm": f"Failed to register device: {str(e)}"})


# Get the client's IP address from the request.
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
