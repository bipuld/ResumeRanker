class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "candidate"


class IsRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "recruiter"