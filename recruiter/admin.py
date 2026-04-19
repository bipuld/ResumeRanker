from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Company, CompanyMember, Job, Application


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
        "id",
        "user",
        "company",
        "role",
        "invite_email",
        "invite_status",
        "is_active",
        "is_approved",
    )

    list_filter = (
        "role",
        "invite_status",
        "is_active",
        "is_approved",
        "company",
    )

    search_fields = (
        "user__email",
        "invite_email",
        "company__name",
    )

    readonly_fields = (
        "invite_token",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("User Info", {
            "fields": ("user", "invite_email", "company")
        }),
        ("Role & Status", {
            "fields": ("role", "invite_status", "is_active", "is_approved", "designation")
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
        ("Invite System", {
            "fields": ("invite_token",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

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


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "company",
        "created_by",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "company__name",
        "created_by__email",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    fieldsets = (
        ("Job Info", {
            "fields": ("company", "title", "description", "location")
        }),
        ("Meta", {
            "fields": ("created_by", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "candidate",
        "job",
        "status",
        "score",
        "created_at",
    )

    list_filter = (
        "status",
        "job",
        "created_at",
    )

    search_fields = (
        "candidate__email",
        "candidate__username",
        "job__title",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    fieldsets = (
        ("Candidate Info", {
            "fields": ("candidate", "job")
        }),
        ("Application Status", {
            "fields": ("status", "score")
        }),
        ("Meta", {
            "fields": ("created_at",)
        }),
    )