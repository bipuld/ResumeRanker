from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserSession

from django.contrib.sessions.models import Session


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "email",
        "username",
        "full_name",
        "is_active",
        "is_verified",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_verified",
        "is_email_verified",
        "is_phone_verified",
        "mfa_enabled",
    )
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    readonly_fields = ("created_at", "updated_at", "password_changed_date")

    fieldsets = (
        (_("Basic Info"), {"fields": ("email", "username", "password")}),
        (
            _("Personal Details"),
            {"fields": ("first_name", "middle_name", "last_name", "phone")},
        ),
        (
            _("Verification Flags"),
            {
                "fields": (
                    "is_email_verified",
                    "is_phone_verified",
                    "is_verified",
                    "social_only",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Security"), {"fields": ("mfa_enabled", "password_changed_date")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            _("Create User"),
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )