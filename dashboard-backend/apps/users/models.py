from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.hashers import make_password
from apps.users.managers import UserManager


class Role(models.Model):
    class Names(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        ADMIN      = "admin",      "Admin"
        MANAGER    = "manager",    "Manager"
        ANALYST    = "analyst",    "Analyst"
        VIEWER     = "viewer",     "Viewer"

    name = models.CharField(max_length=50, unique=True,
                            choices=Names.choices)

    class Meta:
        managed  = False
        db_table = "roles"
        ordering = ["id"]

    def __str__(self):
        return self.name

    # Role hierarchy: higher index = more privileged
    HIERARCHY = ["viewer", "analyst", "manager", "admin", "superadmin"]

    def is_above(self, other_role_name: str) -> bool:
        try:
            return (self.HIERARCHY.index(self.name)
                    > self.HIERARCHY.index(other_role_name))
        except ValueError:
            return False


class UserSector(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        managed  = False
        db_table = "user_sectors"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    Maps to the `users` table. Uses AbstractBaseUser so Django's
    password hashing ecosystem (check_password, set_password, hashers)
    works against the password_hash column.
    managed=False: table already exists on Neon.
    """
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255)
    email      = models.EmailField(unique=True, db_index=True)
    phone      = models.CharField(max_length=30, null=True, blank=True)

    # Maps AbstractBaseUser's `password` field to `password_hash` column
    password   = models.TextField(db_column="password_hash")

    role       = models.ForeignKey(Role,       on_delete=models.PROTECT,
                                   related_name="users")
    sector     = models.ForeignKey(UserSector, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="users")
    manager    = models.ForeignKey("self", on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name="direct_reports")
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    class Meta:
        managed  = False
        db_table = "users"
        ordering = ["last_name", "first_name"]
        indexes  = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["manager"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def role_name(self):
        return self.role.name if self.role_id else None

    def get_reportees(self):
        """Recursively get all users in this manager's tree."""
        direct = list(self.direct_reports.filter(is_active=True))
        all_reports = list(direct)
        for report in direct:
            all_reports.extend(report.get_reportees())
        return all_reports


class UserSession(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name="sessions")
    login_at   = models.DateTimeField(auto_now_add=True)
    logout_at  = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        managed  = False
        db_table = "user_sessions"
        ordering = ["-login_at"]
        indexes  = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["login_at"]),
        ]

    def __str__(self):
        return f"Session {self.user.email} @ {self.login_at}"


class UserClient(models.Model):
    """
    Links a dashboard user to a Safex company they are allowed to see.
    company_id references the Safex `companies` table (cross-app FK).
    """
    user        = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name="client_assignments")
    company_id  = models.IntegerField(db_index=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "user_clients"
        unique_together = [("user", "company_id")]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["company_id"]),
        ]

    def get_company(self):
        from apps.safex.models import Company
        try:
            return Company.objects.get(id=self.company_id)
        except Company.DoesNotExist:
            return None
