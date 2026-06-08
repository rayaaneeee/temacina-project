# API filters for users
from django_filters import rest_framework as filters
from apps.users.models import User


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ["role__name", "sector_id", "manager_id", "is_active"]
