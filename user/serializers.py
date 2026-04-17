import json
import re
from base64 import urlsafe_b64decode

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from utils.services import register_fcm_device
from utils.email import cleanup_email


from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "first_name",
            "middle_name",
            "last_name",
            "is_staff",
            "full_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_name"]




class UserSignUpSerializer(serializers.ModelSerializer):
    """Serializer for user signup with email or phone."""

    email = serializers.EmailField(allow_blank=False, required=False)
    phone = serializers.CharField(allow_blank=False, required=False)
    full_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "middle_name",
            "last_name",
            "phone",
            "full_name",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, password):
        pattern = r"^(?=.*?\d)(?=.*?[A-Z])(?=.*?[#?!@$%^&*\"\'()\\/{}]).{8,}$"
        if not re.match(pattern, password):
            raise ValidationError(
                {
                    "message": "Password must be at least 8 characters long and contain:\n"
                    "- at least 1 numeric character\n"
                    "- at least 1 uppercase letter\n"
                    "- at least 1 special character [#?!@$%^&*\"'()\\/{}]"
                }
            )
        return password

    def validate_email(self, email):
        if not email:
            raise ValidationError({"message": "Email address is required."})
        email = cleanup_email(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError({"message": "User with email already exist"})
        return email

    def validate_phone(self, phone):
        if not phone:
            raise ValidationError({"message": "Phone number is required."})

        if phone[0] != "+":
            phone = f"+{phone}"

        # if User.objects.filter(phone=phone).exists():
        #     raise ValidationError(
        #         {"message": "A user with this phone number already exists."}
        #     )

        if phone.startswith("+977"):
            phone_pattern = r"^\+977(?:984|985|986|974|975|980|981|982|961|962|988|972|963|970)\d{4,12}$"
            if not re.match(phone_pattern, phone):
                raise ValidationError({"message": "Invalid Nepal phone number format."})
        return phone

    def validate(self, data):
        if not data.get("email") and not data.get("phone"):
            raise ValidationError(
                {"message": "Either email or phone number is required."}
            )

        # full name split in to the first and last name
        if data.get("full_name"):
            full_name = data.pop("full_name").strip()
            name_parts = full_name.split()

            if len(name_parts) >= 1:
                data["first_name"] = name_parts[0]
            if len(name_parts) >= 2:
                data["last_name"] = " ".join(name_parts[1:])
        return data

    def create(self, validated_data: dict) -> User:
        """
        Create and return a new User instance with hashed password.
        Username is set to email if present, otherwise phone.
        """
        password = validated_data.pop("password")
        validated_data["role"] = "candidate"
        user = User(**validated_data)
        user.set_password(password)
        user.username = validated_data.get("email") or validated_data.get("phone")
        user.save()


        # Assign user to 'Student' group
        try:
            student_group = Group.objects.get(name="candidate")
            user.groups.add(student_group)
        except Group.DoesNotExist:
            pass  # Handle case where Student group doesn't exist

        # Optionally generate verification token or UID here
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        return user


class UserLoginSerializer(serializers.ModelSerializer):
    fcm_token = serializers.CharField(required=False, allow_null=True)
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


    class Meta:
        model = User
        fields = ("id", "email", "password", "is_verified", "fcm_token")
        read_only_fields = (
            "id",
            "is_verified",
        )

    def validate(self, attrs: dict[str, str]):
        email = attrs.get("email")

        if not email:
            raise ValidationError({"message": "Email is required."})

        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError({"message": "Enter a valid email address."})

        
        # Create queryset to find the user by email (case-insensitive)
        attrs["queryset"] = {"email__iexact": email}
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        queryset = validated_data.pop("queryset")
        password = validated_data.pop("password")
        fcm_token = validated_data.pop("fcm_token", None)

        try:
            user = User.objects.get(**queryset)
        except User.DoesNotExist:
            raise ValidationError(
                {"message": "No account found with these credentials."}
            )
        if not user.is_verified:
            raise ValidationError({"message": "Please verify your email first"})

        if not user.check_password(password):
            raise ValidationError(
                {"message": "Credential does not match. Please try again."}
            )

        if not user.is_active:
            user.is_active = True
            user.save()

        # if fcm_token:
        #     pass
        #     register_fcm_device(user, self.context["request"])
        return user


class TokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh: RefreshToken = self.token_class(attrs["refresh"])
        user: User = User.objects.get(id=refresh.payload["user_id"])
        if refresh.payload["iat"] < user.password_changed_date.timestamp():
            raise serializers.ValidationError(
                {"message": "This token has already been expired."}
            )
        return super().validate(attrs)






class PasswordChangeSerializer(serializers.Serializer):
    social_token = serializers.CharField(allow_null=True, required=False)
    old_password = serializers.CharField(
        allow_null=True,
    )
    new_password = serializers.CharField(
        min_length=8,
        max_length=128,
    )
    confirm_password = serializers.CharField(min_length=8, max_length=128)

    @staticmethod
    def validate_password_length(value):
        if len(value) < getattr(settings, "PASSWORD_MIN_LENGTH", 8):
            raise ValidationError(
                {
                    "message": "Password should be at least %s characters long."
                    % getattr(settings, "PASSWORD_MIN_LENGTH", 8)
                },
                status.HTTP_400_BAD_REQUEST,
            )
        return value

    def validate_old_password(self, password: str):
        user: User = self.context["request"].user
        if not password:
            return password
        if not user.check_password(password):
            raise ValidationError(
                {"message": "The old password you have entered is incorrect"}
            )
        return password

    def validate_new_password(self, value):
        self.validate_password_length(value)
        if not re.match(r"^(?=.*?\w)(?=.*?[#?!@$%^&*\"'()\\/{}]).{8,}$", value):
            raise ValidationError(
                {
                    "message": "The password must be at least 8 characters long with\n"
                    "1. at least 1 numeric character\n"
                    "2. one capital case and\n"
                    "3. one special character among [#?!@$%^&*\"'()\\/{}]"
                }
            )
        return value

    def validate(self, attrs):
        if attrs.get("social_token"):
            try:
                social_token = attrs["social_token"].split(".")[1]
                data = json.loads(
                    urlsafe_b64decode(social_token.encode() + b"==").decode()
                )
            except (IndexError, UnicodeDecodeError):
                raise ValidationError({"message": "Invalid social token."})

            attrs["old_password"] = data["jti"]
        else:
            if not attrs.get("old_password"):
                raise ValidationError({"message": ["Password cannot be null."]})
            if attrs.get("new_password") != attrs.get("confirm_password"):
                raise ValidationError(
                    {"message": ["Password and Confirm password does not match."]}
                )
        if attrs["old_password"] == attrs["new_password"]:
            raise ValidationError(
                {"message": ["You have entered the same password as old password"]}
            )
        if attrs.get("social_token"):
            self.context["request"].user.social_only = False
            self.context["request"].user.save()
        return attrs


class ForgetPasswordLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = "email"

    def validate(self, data):
        if not data.get("email"):
            raise ValidationError({"message": "Email address is required."})

        return data

    def validate_email(self, email):
        email = cleanup_email(email)
        try:
            user = User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            raise ValidationError({"message": "No User exists with this email."})

    def create(self, validated_data):
        user = User.objects.get(email=validated_data["email"])

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user=user)

        request = self.context.get("request")
        app_domain = f"{request.scheme}://{request.get_host()}" if request else settings.APP_DOMAIN

        context = {
            "user": user,
            "user_name": user.get_full_name() or user.first_name or user.email,
            "link": f"{app_domain}/password/reset-confirm/?u={uid}&t={token}",
        }

        html_content = render_to_string("email/user_reset_email.html", context)

        send_mail(
            subject="ResumeRanker - Password Reset Link",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )

        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(
        write_only=True, min_length=8, required=False
    )

    def validate_new_password(self, value):
        """Validate new password strength"""
        if len(value) < 8:
            raise serializers.ValidationError(
                {"message": "Password must be at least 8 characters long."}
            )

        # Check for at least one uppercase letter, one digit, and one special character
        pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[#?!@$%^&*\"'()\\/{}]).{8,}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                {
                    "message": "Password must contain at least 8 characters including:\n"
                    "- At least 1 uppercase letter\n"
                    "- At least 1 digit\n"
                    "- At least 1 special character [#?!@$%^&*\"'()\\/{}]"
                }
            )
        return value

    def validate(self, data):

        if (
            data.get("confirm_password")
            and data["new_password"] != data["confirm_password"]
        ):
            raise serializers.ValidationError({"message": "Passwords do not match."})
        try:
            uid = urlsafe_base64_decode(data["uid"]).decode()
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError({"message": "Invalid user ID."})

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError(
                {"message": "Invalid or expired reset token."}
            )

        return data

    def save(self, **kwargs):
        """Save the new password for the user"""
        self.user.set_password(self.validated_data["new_password"])

        if hasattr(self.user, "password_changed_date"):
            self.user.password_changed_date = timezone.now()

        self.user.save()
        return self.user


class UserLogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.
    It only requires the refresh token to blacklist it on logout.
    """

    refresh = serializers.CharField(
        help_text="Refresh token to be used for logout.",
        required=True,
        write_only=True,
    )
