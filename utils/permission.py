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
        return request.user.is_staff or obj.owner == request.user


