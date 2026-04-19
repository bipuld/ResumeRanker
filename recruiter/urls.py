
from rest_framework.routers import DefaultRouter
from .api import (
    CompanyViewSet,
    CompanyAdminViewSet,
    InviteMemberView,
    AcceptInviteView,
    JobCreateView,
    ApplyJobView,
    UpdateApplicationView,
    CompanyMemberListView,
    CompanyMemberUpdateView,
    CompanyMemberDeleteView,
    ResendInviteView,
    PendingInvitesView,
)
from django.urls import path

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'admin/companies', CompanyAdminViewSet, basename='admin-companies')
urlpatterns = [
    
    path(
        "company/<uuid:company_id>/invite/",
        InviteMemberView.as_view(),
        name="company-invite"
    ),

    # 📬 Accept invite
    path(
        "company/invite/<uuid:token>/accept/",
        AcceptInviteView.as_view(),
        name="accept-invite"
    ),

    # 👥 List members
    path(
        "company/<uuid:company_id>/members/",
        CompanyMemberListView.as_view(),
        name="company-members"
    ),

    # ✏️ Update member role
    path(
        "company/member/<uuid:pk>/",
        CompanyMemberUpdateView.as_view(),
        name="update-member"
    ),

    # ❌ Remove member
    path(
        "company/member/<uuid:pk>/delete/",
        CompanyMemberDeleteView.as_view(),
        name="delete-member"
    ),

    # 🔁 Resend invite
    path(
        "company/member/<uuid:pk>/resend-invite/",
        ResendInviteView.as_view(),
        name="resend-invite"
    ),

    # 📊 Pending invites list
    path(
        "company/<uuid:company_id>/invites/",
        PendingInvitesView.as_view(),
        name="pending-invites"
    ),

    
]


urlpatterns = router.urls + urlpatterns