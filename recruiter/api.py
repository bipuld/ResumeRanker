from rest_framework import viewsets
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from recruiter.models import Company
from recruiter.serializers import CompanySerializer, CompanyMemberSerializer, ApplicationSerializer, JobSerializer
from utils.permission import IsOwnerOrAdmin,IsAdminUserOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from .models import CompanyMember, Application


def can_post_jobs(user, company):
    return CompanyMember.objects.filter(
        user=user,
        company=company,
        is_active=True,
        can_post_jobs=True,
    ).exists()

# class CompanyViewSet(viewsets.ModelViewSet):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer

#     def get_permissions(self):
#         if self.action in ["list", "retrieve"]:
#             return [AllowAny()]
#         return [IsAuthenticated(), IsOwnerOrAdmin()]

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

#     def get_queryset(self):
#         user = self.request.user

#         if user.is_authenticated:
#             return Company.objects.filter(owner=user)
#         return Company.objects.filter(is_active=True, is_verified=True)

#     def get_object(self):
#         obj = super().get_object()
#         self.check_object_permissions(self.request, obj)
#         return obj


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    # ✅ FIXED QUERYSET (VERY IMPORTANT)
    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            # companies where user is owner OR member
            return Company.objects.filter(
                Q(owner=user) |
                Q(members__user=user)
            ).distinct()

        return Company.objects.filter(is_active=True, is_verified=True)

    def perform_create(self, serializer):
        company = serializer.save(owner=self.request.user)

        CompanyMember.objects.create(
            user=self.request.user,
            company=company,
            role="owner",
            invite_email=self.request.user.email,
            invite_status="accepted",
            is_active=True, 
            is_approved=False,  

            can_post_jobs=True,
            can_edit_jobs=True,
            can_delete_jobs=True,
            can_view_applicants=True,
            can_shortlist_candidates=True,
            can_manage_team=True,

            designation=f"Owner of {company.name}"
        )

class CompanyAdminViewSet(viewsets.ModelViewSet):
    "Admin-only viewset for managing companies"
    queryset = Company.objects.all().order_by("-created_at")
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUserOnly]

    # ✅ List + Filter
    def get_queryset(self):
        queryset = super().get_queryset()

        is_verified = self.request.query_params.get("is_verified")

        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == "true")

        return queryset

    # ✅ Retrieve (Already provided by DRF)
    # GET /admin/companies/{id}/

    # ✅ Toggle verification
    @action(detail=True, methods=["patch"])
    def toggle_verification(self, request, pk=None, *args, **kwargs):
        company = self.get_object()

        company.is_verified = not company.is_verified
        company.save()

        return Response({
            "message": f"{company.name} verification updated",
            "is_verified": company.is_verified
        }, status=status.HTTP_200_OK)




# Company owner members, jobs, applications etc. through separate viewsets which we will create next.


class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = kwargs.get("company_id")
        email = request.data.get("email")
        role = request.data.get("role", "recruiter")

        # 1. Get company safely
        company = get_object_or_404(Company, id=company_id)

        # 2. Create invite member (user is NOT set for invite)
        member = CompanyMember.objects.create(
            company=company,
            invite_email=email,
            role=role,
            is_approved=False,
            is_active=False
        )

        # 3. Invite link
        invite_link = f"{settings.FRONTEND_URL}/login/{member.invite_token}"

        # 5. Email context
        context = {
            "company": company,
            "role": role,
            "invite_link": invite_link,
            "user": request.user, 
            "user_name": request.user.get_full_name() or request.user.email,
        }

        html_content = render_to_string(
            "email/member_invitation.html",
            context
        )

        # 6. Send email
        send_mail(
            subject=f"You're invited to join {company.name}",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
         
        )

        return Response({"message": "Invite sent successfully"})


class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, token):
        return Response(
            {
                "message": "Invitation link is valid. Sign in and send POST to this same URL to accept.",
                "token": str(token),
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, token):
        member = CompanyMember.objects.get(invite_token=token)

        if member.invite_email != request.user.email:
            return Response({"error": "Email mismatch"}, status=403)

        member.user = request.user
        member.invite_status = "accepted"
        member.is_active = True
        member.save()

        return Response({"message": "Joined company"})




class JobCreateView(generics.CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        company = serializer.validated_data["company"]

        if not can_post_jobs(self.request.user, company):
            raise PermissionDenied("Not allowed")

        serializer.save(created_by=self.request.user)

class ApplyJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)


class UpdateApplicationView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]


class CompanyMemberListView(generics.ListAPIView):
    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CompanyMember.objects.filter(company_id=self.kwargs["company_id"])


class CompanyMemberUpdateView(generics.UpdateAPIView):
    queryset = CompanyMember.objects.all()
    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]


class CompanyMemberDeleteView(generics.DestroyAPIView):
    queryset = CompanyMember.objects.all()
    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]


class ResendInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        member = CompanyMember.objects.get(pk=pk)

        invite_link = f"{settings.FRONTEND_URL}/login/{member.invite_token}"
        context = {
            "company": member.company,
            "role": member.role,
            "invite_link": invite_link,
            "user_name": request.user.get_full_name() or request.user.email,
        }

        html_content = render_to_string("email/member_invitation.html", context)

        send_mail(
            subject=f"You're invited to join {member.company.name}",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member.invite_email],
            html_message=html_content,
            fail_silently=False,
        )

        return Response({"message": "Invite resent successfully"}, status=status.HTTP_200_OK)


class PendingInvitesView(generics.ListAPIView):
    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CompanyMember.objects.filter(
            company_id=self.kwargs["company_id"],
            invite_status="pending",
        )