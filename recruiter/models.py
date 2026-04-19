import uuid
from django.db import models
from utils.common_model import CommonModel
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth import get_user_model

User = get_user_model()



class Company(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = CKEditor5Field("description", config_name="extends", blank=False)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)

    industry = models.CharField(max_length=255, blank=True, null=True)
    size = models.CharField(
        max_length=50,
        choices=[
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("200+", "200+ employees"),
        ],
        blank=True,
        null=True,
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_companies"
    )
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    contact_person_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_person_designation = models.CharField(max_length=255, blank=True, null=True)

    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Nepal")
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CompanyMember(CommonModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="company_memberships",
        null=True,
        blank=True
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="members"
    )

    # ROLE INSIDE COMPANY (VERY IMPORTANT)
    role = models.CharField(
        max_length=50,
        choices=[
            ("owner", "Owner"),
            ("admin", "Admin"),
            ("hr", "HR Manager"),
            ("recruiter", "Recruiter"),
            ("interviewer", "Interviewer"),
        ],
        default="recruiter"
    )

    #  PERMISSIONS
    can_post_jobs = models.BooleanField(default=True)
    can_edit_jobs = models.BooleanField(default=False)
    can_delete_jobs = models.BooleanField(default=False)

    can_view_applicants = models.BooleanField(default=True)
    can_shortlist_candidates = models.BooleanField(default=True)

    can_manage_team = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    designation = models.CharField(max_length=255, blank=True, null=True)

    # INVITE SYSTEM
    invite_email = models.EmailField()
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True)
    invite_status = models.CharField(max_length=20, default="pending")

    is_active = models.BooleanField(default=False)
    

    class Meta:
        unique_together = ("user", "company")
    def save(self, *args, **kwargs):
        is_new_verification = False

        if self.pk:
            old = Company.objects.get(pk=self.pk)
            if not old.is_verified and self.is_verified:
                is_new_verification = True

        super().save(*args, **kwargs)

        # 🔥 when company becomes verified
        if is_new_verification:
            self.members.filter(role="owner").update(
                is_approved=True
            )
    def __str__(self):
        return f"{self.user.email} - {self.company.name} ({self.role})"



# models/job.py
class Job(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class Application(CommonModel):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("hired", "Hired"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    score = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"{self.candidate.username} - {self.job.title} ({self.status})"