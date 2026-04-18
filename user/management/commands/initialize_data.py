import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Initialize ResumeRanker with default data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force initialization even if data exists",
        )

    @staticmethod
    def create_groups():
        """Create default user groups for the ResumeRanker with specific PKs"""
        groups = ["Superuser", "Admin", "Recruiter", "Staff", "Candidate"]
        for index, name in enumerate(groups, start=1):
            Group.objects.update_or_create(pk=index, defaults={"name": name})
        # Permission CSV integration can be added later if needed

    def create_users(self):
        """Create superuser only"""
        try:
            User.objects.get(username="admin")
        except User.DoesNotExist:
            admin_user = User(
                username="admin",
                email="ats@gmail.com",
                first_name="System",
                last_name="Administrator",
                role="admin",
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            admin_user.set_password("ats_admin@11")
            admin_user.save()
            try:
                superuser_group = Group.objects.get(name="Superuser")
                admin_user.groups.add(superuser_group)
            except Group.DoesNotExist:
                pass

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.create_groups()
                self.create_users()
        except Exception as e:
            raise e
