from rest_framework.permissions import BasePermission

HIERARCHY = ["viewer", "analyst", "manager", "admin", "superadmin"]


def _rank(role_name: str) -> int:
    try:
        return HIERARCHY.index(role_name)
    except ValueError:
        return -1


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role_name == "superadmin")


class IsAdminOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and _rank(request.user.role_name) >= _rank("admin"))


class IsManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and _rank(request.user.role_name) >= _rank("manager"))


class IsAnalystOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and _rank(request.user.role_name) >= _rank("analyst"))


class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class CanManageUser(BasePermission):
    """
    A manager can only edit/delete users they manage directly.
    Admins and above can manage anyone below their level.
    """
    def has_object_permission(self, request, view, obj):
        actor = request.user
        if _rank(actor.role_name) >= _rank("admin"):
            return _rank(actor.role_name) > _rank(obj.role_name)
        if actor.role_name == "manager":
            return obj.manager_id == actor.id
        return False


class CanAccessCompany(BasePermission):
    """
    Viewers and Analysts can only access companies assigned to them
    via user_clients. Managers and above see all.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if _rank(user.role_name) >= _rank("manager"):
            return True
        # obj is a Company; check user_clients
        return user.client_assignments.filter(
            company_id=obj.id
        ).exists()
