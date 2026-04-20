from rest_framework import serializers
from .models import Company, CompanyMember, Application, Job


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id", "owner", "is_verified"]


class CompanyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMember
        fields = "__all__"
        read_only_fields = ("user", "invite_token", "invite_status", "is_active")


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("candidate", "score")

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ("company", "created_by")

class UserCompanyFullSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = CompanyMember
        fields = [
            "id",
            "role",
            "designation",
            "is_active",
            "invite_status",
            "is_owner",
            "company",
        ]

    def get_company(self, obj):
        return {
            "id": obj.company.id,
            "name": obj.company.name,
            "location": obj.company.location,
            "industry": obj.company.industry,
            "size": obj.company.size,
            "is_verified": obj.company.is_verified,
            "logo": obj.company.logo.url if obj.company.logo else None,
        }

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return (
            obj.company.owner == request.user
            or obj.role == "owner"
        )
