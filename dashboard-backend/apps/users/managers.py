from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password, first_name, last_name,
                    role_id, **extra):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        email = self.normalize_email(email)
        user  = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            **extra,
        )
        user.set_password(password)   # bcrypt via Django hashers
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name="Admin",
                         last_name="User", **extra):
        from apps.users.models import Role
        admin_role = Role.objects.get(name=Role.Names.SUPERADMIN)
        extra.setdefault("is_staff",     True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active",    True)
        return self.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            role_id=admin_role.id, **extra,
        )

    def active(self):
        return self.filter(is_active=True)

    def by_role(self, role_name: str):
        return self.filter(role__name=role_name, is_active=True)
