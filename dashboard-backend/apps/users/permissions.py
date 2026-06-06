from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class IsManagerOrAbove(BasePermission):
    ALLOWED = {"admin", "manager"}
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED

class IsAnalystOrAbove(BasePermission):
    ALLOWED = {"admin", "manager", "analyst"}
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED
