
from rest_framework.routers import DefaultRouter
from .api import (
    CompanyViewSet,
    CompanyAdminViewSet,
    InviteMemberView,

    JobCreateView,
    ApplyJobView,
    UpdateApplicationView,
    CompanyMemberListView,
    CompanyMemberUpdateView,
    CompanyMemberDeleteView,
    PendingInvitesView,
    UserCompanyMembershipDetailsView
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


    path("member/details/", UserCompanyMembershipDetailsView.as_view()),


    # 👥 List members
    path(
        "company/<uuid:company_id>/members/",
        CompanyMemberListView.as_view(),
        name="company-members"
    ),

    # ✏️ Update member role
    path(
        "company/member/<int:pk>/",
        CompanyMemberUpdateView.as_view(),
        name="update-member"
    ),

    # ❌ Remove member
    path(
        "company/member/<int:pk>/delete/",
        CompanyMemberDeleteView.as_view(),
        name="delete-member"
    ),
    # 📊 Pending invites list
    path(
        "company/<uuid:company_id>/invites/",
        PendingInvitesView.as_view(),
        name="pending-invites"
    ),

    
]


urlpatterns = router.urls + urlpatterns