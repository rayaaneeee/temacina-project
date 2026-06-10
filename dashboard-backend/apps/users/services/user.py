from django.core.cache import cache
from apps.users.models import User, Role, UserSector, UserClient
from apps.audit.services import write_log


class UserService:

    CACHE_TTL = 300

    @staticmethod
    def get_all(filters=None) -> "QuerySet":
        qs = (
            User.objects
            .select_related("role", "sector", "manager")
            .filter(is_active=True)
        )
        if filters:
            if filters.get("role"):
                qs = qs.filter(role__name=filters["role"])
            if filters.get("sector_id"):
                qs = qs.filter(sector_id=filters["sector_id"])
            if filters.get("manager_id"):
                qs = qs.filter(manager_id=filters["manager_id"])
        return qs

    @staticmethod
    def get_by_id(user_id: int) -> "User | None":
        key    = f"user:profile:{user_id}"
        cached = cache.get(key)
        if cached:
            return cached
        try:
            user = (User.objects
                    .select_related("role", "sector", "manager")
                    .get(id=user_id, is_active=True))
            cache.set(key, user, UserService.CACHE_TTL)
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def create_user(actor, data: dict) -> "User":
        """
        Actor must be admin or above and cannot create users
        with higher or equal privilege.
        """
        target_role = Role.objects.get(id=data["role_id"])
        if not actor.role.is_above(target_role.name):
            raise PermissionError(
                "You cannot create a user with a role equal "
                "to or higher than yours."
            )
        password = data.pop("password")
        user = User.objects.create_user(password=password, **data)
        write_log(
            user=actor, action="USER_CREATED",
            entity_type="User", entity_id=user.id,
            details={"email": user.email, "role": target_role.name},
        )
        return user

    @staticmethod
    def update_user(actor, target: "User", data: dict) -> "User":
        safe_fields = {"first_name", "last_name", "phone",
                       "sector_id", "manager_id"}
        if actor.role.name in ("admin", "superadmin"):
            safe_fields.add("role_id")
            safe_fields.add("is_active")
        for field, value in data.items():
            if field in safe_fields:
                setattr(target, field, value)
        target.save()
        cache.delete(f"user:profile:{target.id}")
        write_log(
            user=actor, action="USER_UPDATED",
            entity_type="User", entity_id=target.id,
            details={"changed_fields": list(data.keys())},
        )
        return target

    @staticmethod
    def deactivate_user(actor, target: "User"):
        if not actor.role.is_above(target.role_name):
            raise PermissionError("Insufficient privilege to deactivate this user.")
        target.is_active = False
        target.save(update_fields=["is_active"])
        cache.delete(f"user:profile:{target.id}")
        write_log(
            user=actor, action="USER_DELETED",
            entity_type="User", entity_id=target.id,
            details={"email": target.email},
        )

    @staticmethod
    def change_role(actor, target: "User", new_role_name: str):
        if not actor.role.is_above(new_role_name):
            raise PermissionError("Cannot assign a role equal to or above your own.")
        new_role = Role.objects.get(name=new_role_name)
        old_role = target.role_name
        target.role = new_role
        target.save(update_fields=["role_id"])
        cache.delete(f"user:profile:{target.id}")
        write_log(
            user=actor, action="ROLE_CHANGED",
            entity_type="User", entity_id=target.id,
            details={"from": old_role, "to": new_role_name},
        )

    @staticmethod
    def assign_company(user: "User", company_id: int, actor):
        obj, created = UserClient.objects.get_or_create(
            user=user, company_id=company_id
        )
        if not created:
            raise ValueError("Company already assigned to this user.")
        write_log(
            user=actor, action="COMPANY_VIEWED",
            entity_type="UserClient", entity_id=obj.id,
            details={"company_id": company_id, "assigned_to": user.id},
        )
        return obj

    @staticmethod
    def get_direct_reports(manager_id: int):
        return (
            User.objects
            .filter(manager_id=manager_id, is_active=True)
            .select_related("role", "sector")
        )

    @staticmethod
    def get_assigned_companies(user: "User"):
        from apps.safex.models import Company
        company_ids = user.client_assignments.values_list("company_id", flat=True)
        return Company.objects.filter(id__in=company_ids)
