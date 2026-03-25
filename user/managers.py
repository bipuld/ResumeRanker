from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group


class UserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        return (email or "").lower()

    def _create_user(self, role=None, **kwargs):
        password = kwargs.pop("password", None)

        if not (kwargs.get("email") or kwargs.get("phone") or kwargs.get("username")):
            raise ValueError("Username, phone, or email must be provided")

        if kwargs.get("email"):
            kwargs["email"] = self.normalize_email(kwargs["email"])

        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)

        # Assign role group if provided
        if role:
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        return user

    def create_user(self, role=None, **kwargs):
        kwargs.setdefault("is_superuser", False)
        kwargs.setdefault("is_staff", False)
        return self._create_user(role=role, **kwargs)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        role = "Superuser"

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(
            username=username, password=password, role=role, **extra_fields
        )
