from django.db import models

# Create your models here.
import json
import re
import sys
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as RestValidationError
from django.contrib.sessions.models import Session
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


from utils.common_model import CommonModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    username = models.CharField(_("username"), max_length=255, unique=True)
    phone = models.CharField(
        max_length=17,
        validators=[
            RegexValidator(
                regex=r"^\+?[1-9][0-9]{7,14}$",
                message="The contact number can have + sign in the beginning and max 15 digits without delimiters",
            )
        ],
        null=True,
        blank=True,
    )
    first_name = models.CharField(_("first name"), max_length=64, null=True, blank=True)
    middle_name = models.CharField(
        _("middle name"), max_length=64, null=True, blank=True
    )
    last_name = models.CharField(_("last name"), max_length=64, null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Active Status")
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, verbose_name="Verified Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mfa_enabled = models.BooleanField(
        default=False,
        help_text="Multi factor authentication enabled",
    )
    social_only = models.BooleanField(
        default=False,
        help_text="For login with social auth.",
    )
    is_staff = models.BooleanField(default=False)
    password_changed_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("-created_at", "first_name")
        permissions = (("view_user_analytics", "Can view user analytics"),)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return re.sub(
            r"\s{2,}",
            " ",
            f'{self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}',
        ).strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def clean(self):
        super().clean()
        self.username = self.username.lower()
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def full_name(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            super().save(*args, **kwargs)
        except (ValidationError, IntegrityError) as e:
            raise RestValidationError(e) from e

    # Session limit handling
    def get_active_sessions(self):
        return self.user_sessions.filter(
            is_active=True, expires_at__gt=timezone.now()
        ).order_by("-last_activity")

    # def enforce_session_limit(self, exclude_session_key=None):
    #     max_sessions = getattr(settings, "SESSION_MAX_CONCURRENT_SESSIONS", 2)
    #     active_sessions = self.get_active_sessions()
    #     if exclude_session_key:
    #         active_sessions = active_sessions.exclude(session_key=exclude_session_key)
    #     if active_sessions.count() >= max_sessions:
    #         sessions_to_deactivate = active_sessions[max_sessions - 1 :]
    #         for session in sessions_to_deactivate:
    #             session.deactivate()
    def enforce_session_limit(self, exclude_session_key=None):
        """
        Enforce concurrent session limit.
        Deactivates oldest sessions if limit is exceeded.
        """
        max_sessions = getattr(settings, "SESSION_MAX_CONCURRENT_SESSIONS", 5)
        active_sessions = self.get_active_sessions()
        
        if exclude_session_key:
            active_sessions = active_sessions.exclude(session_key=exclude_session_key)
        
        # If we're at or over the limit, deactivate the oldest sessions
        sessions_over_limit = active_sessions.count() - max_sessions + 1
        
        if sessions_over_limit > 0:
            sessions_to_deactivate = active_sessions.order_by('last_activity')[:sessions_over_limit]
            
            for session in sessions_to_deactivate:
                session.deactivate()
                print(f"Deactivated session {session.session_key} for user {self.username} due to session limit")

    def deactivate_all_other_sessions(self, current_session_key):
        """Deactivate all sessions except the current one."""
        other_sessions = self.user_sessions.filter(
            is_active=True
        ).exclude(session_key=current_session_key)
        
        for session in other_sessions:
            session.deactivate()
            print(f"Deactivated session {session.session_key} for user {self.username}")



# class UserProfile(CommonModel):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
#     bio = CKEditor5Field("Bio", config_name="extends", blank=True)
#     profile_image = models.ImageField(
#         upload_to=profile_image_upload_to,
#         null=True,
#         blank=True,
#         help_text="Upload a profile picture",
#     )
#     gender = models.CharField(
#         max_length=60, choices=GenderChoice, default=GenderChoice.male
#     )
#     dob = models.DateField(
#         blank=False, null=False, help_text="Date of Birth in AD"
#     )  # date_of_birth
#     current_address = models.CharField(max_length=100)
#     permanent_address = models.CharField(max_length=100)
#     language = models.CharField(
#         max_length=100, null=True, blank=True
#     )  # the language they spoke
#     is_profile_verified = models.BooleanField(
#         default=False, help_text="Indicates user if verified or not "
#     )  # In future to check if user profile is subscribed
#     nepali_dob = models.CharField(
#         blank=True,
#         null=True,
#         help_text="Date of Birth in BS",
#         verbose_name="Nepali Date of Birth",
#     )

#     class Meta:
#         verbose_name = _("user profile")
#         verbose_name_plural = _("user profiles")
#         ordering = ("-created_at",)

#     def save(self, *args, **kwargs):
#         if self.dob:
#             self.nepali_dob = str(nepali_datetime.date.from_datetime_date(self.dob))
#             print(f"Date of Birth in Nepali: {self.nepali_dob}")
#         else:
#             print("Date of Birth is not set for this user profile.")
#         return super().save(*args, **kwargs)

#     def get_dob_bs(self):
#         """
#         Returns the date of birth in BS format fully in Nepali (Devanagari script).
#         """
#         if self.dob:
#             nepali_date = nepali_datetime.date.from_datetime_date(self.dob)
#             formatted_date = nepali_date.strftime("%K %B %d")
#             print(f"Date of Birth in Nepali: {formatted_date}")
#             return formatted_date
#         print("Date of Birth is not set for this user profile.")
#         return None

#     def __str__(self):
#         return f"{self.user.first_name}"




class UserSession(models.Model):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="user_sessions"
    )
    session_key = models.CharField(max_length=40, unique=True)
    device_info = models.JSONField(
        default=dict,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(
        null=True, blank=True, help_text="User agent string of the browser or device"
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Session expiration time"
    )
    token_jti = models.CharField(max_length=255, null=True, blank=True, help_text="JTI of refresh token for this session")

    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("user session")
        verbose_name_plural = _("user sessions")
        ordering = ("-last_activity",)
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["session_key"]),
            models.Index(fields=["expires_at"]),
        ]

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])

        # Delete the Django session
        Session.objects.filter(session_key=self.session_key).delete()
        print(f"Session {self.session_key} deactivated and deleted successfully.")
        print(f"Django session {self.session_key} deleted successfully.")
        if self.token_jti:
            try:
                token = OutstandingToken.objects.get(jti=self.token_jti)
                BlacklistedToken.objects.get_or_create(token=token)
                print(f"Outstanding token {self.token_jti} blacklisted successfully.")
            except OutstandingToken.DoesNotExist:
                print(f"No outstanding token found for jti={self.token_jti}")

    def is_expired(self):
        """Check if the session is expired"""
        return timezone.now() > self.expires_at

    def refresh_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])

    def get_device_name(self):
        """Extract a friendly device name from user agent."""
        user_agent = self.user_agent or ""
        if "Mobile" in user_agent:
            return "Mobile Device"
        elif "Tablet" in user_agent:
            return "Tablet"
        elif "Windows" in user_agent:
            return "Windows PC"
        elif "Mac" in user_agent:
            return "Mac"
        elif "Linux" in user_agent:
            return "Linux PC"
        else:
            return "Unknown Device"

    def __str__(self):
        status = "Active" if self.is_active and not self.is_expired() else "Inactive"
        device = self.get_device_name()
        return f"Session for {self.user.username} - {device} ({status})"


    def __str__(self):
        status = "Active" if self.is_active and not self.is_expired() else "Inactive"
        return (
            f"Session for {self.user.username} - {self.session_key[:10]}... ({status})"
        )
