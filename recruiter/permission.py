from .models import CompanyMember, Job, Application
def get_member(user, company):
    return CompanyMember.objects.filter(user=user, company=company, is_active=True).first()


def can_post_jobs(user, company):
    member = get_member(user, company)
    return member and member.role in ["owner", "admin", "hr", "recruiter"]