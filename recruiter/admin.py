from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Company, CompanyMember


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "industry",
        "city",
        "country",
        "owner",
        "is_verified",
        "is_active",
        "created_at",
    )

    list_filter = (
        "industry",
        "size",
        "is_verified",
        "is_active",
        "country",
        "city",
    )

    search_fields = (
        "name",
        "industry",
        "email",
        "phone",
        "contact_person_name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "latitude",
        "longitude",
    )

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "name",
                "description",
                "website",
                "logo",
                "industry",
                "size",
            )
        }),

        ("Location", {
            "fields": (
                "location",
                "latitude",
                "longitude",
                "address_line1",
                "address_line2",
                "city",
                "state",
                "country",
                "postal_code",
            )
        }),

        ("Contact Info", {
            "fields": (
                "email",
                "phone",
                "contact_person_name",
                "contact_person_email",
                "contact_person_phone",
                "contact_person_designation",
            )
        }),

        ("Ownership", {
            "fields": (
                "owner",
                "is_verified",
                "is_active",
            )
        }),

        ("System Info", {
            "fields": (
                "id",
                "created_at",
            )
        }),
    )

@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "company",
        "role",
        "designation",
        "is_approved",
        "is_active",
        "can_post_jobs",
        "can_view_applicants",
        "created_at",
    )

    list_filter = (
        "role",
        "is_approved",
        "is_active",
        "can_post_jobs",
        "can_manage_team",
        "company",
    )

    search_fields = (
        "user__email",
        "user__username",
        "company__name",
        "designation",
    )

    autocomplete_fields = ("user", "company")

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Member Info", {
            "fields": (
                "user",
                "company",
                "role",
                "designation",
            )
        }),

        ("Permissions", {
            "fields": (
                "can_post_jobs",
                "can_edit_jobs",
                "can_delete_jobs",
                "can_view_applicants",
                "can_shortlist_candidates",
                "can_manage_team",
            )
        }),

        ("Status", {
            "fields": (
                "is_active",
                "is_approved",
            )
        }),

        ("System Info", {
            "fields": (
                "created_at",
            )
        }),
    )