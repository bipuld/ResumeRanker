from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserSession, UserProfile, CandidateProfile

from django.contrib.sessions.models import Session


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "email",
        "username",
        "full_name",
        "role",
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
            {"fields": ("first_name", "middle_name", "last_name", "phone","role")},
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
        (_("OTP Info"), {"fields": ("otp", "otp_created_at", "otp_attempts", "otp_last_sent")}),
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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ("user", "gender", "dob", "is_verified")
    search_fields = ("user__email", "user__username")
    list_filter = ("gender", "is_verified")

    fieldsets = (
        ("User", {
            "fields": ("user",)
        }),

        ("Personal Info", {
            "fields": (
                "bio",
                "profile_image",
                "gender",
                "dob",
                "current_address",
                "permanent_address",
                "language",
            )
        }),

        ("Status", {
            "fields": ("is_verified",)
        }),
    )

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "current_job_title",
        "experience_years",
        "is_profile_complete",
        "is_profile_verified",
    )

    search_fields = (
        "user__email",
        "skills",
        "current_job_title",
        "university",
    )

    list_filter = (
        "is_profile_complete",
        "is_profile_verified",
        "experience_years",
    )

    readonly_fields = ("parsed_resume_text",)

    fieldsets = (
        ("User", {
            "fields": ("user",)
        }),

        ("Resume", {
            "fields": ("resume", "parsed_resume_text", "skills")
        }),

        ("Professional Info", {
            "fields": (
                "experience_years",
                "current_job_title",
                "highest_education",
                "university",
                "location",
            )
        }),

        ("Links", {
            "fields": (
                "linkedin_url",
                "github_url",
                "portfolio_url",
            )
        }),

        ("Status", {
            "fields": (
                "is_profile_complete",
                "is_profile_verified",
            )
        }),
    )

class CandidateProfileInline(admin.StackedInline):
    model = CandidateProfile
    can_delete = False
    extra = 0


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0

class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, CandidateProfileInline]