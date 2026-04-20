from rest_framework.permissions import BasePermission


class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "candidate"


class IsRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "recruiter"


class IsAdminUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        # Works for Company objects (obj.owner) and related objects
        # like CompanyMember/Application/Job (obj.company.owner).
        owner = getattr(obj, "owner", None)
        if owner is not None:
            return owner == user

        company = getattr(obj, "company", None)
        return company is not None and getattr(company, "owner", None) == user


