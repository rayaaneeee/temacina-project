from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import User, Role, UserSector, UserSession, UserClient


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Role
        fields = ["id", "name"]


class UserSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserSector
        fields = ["id", "name"]


class UserListSerializer(serializers.ModelSerializer):
    role    = RoleSerializer(read_only=True)
    sector  = UserSectorSerializer(read_only=True)
    manager = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ["id", "first_name", "last_name", "email",
                  "phone", "role", "sector", "manager",
                  "is_active", "created_at"]

    def get_manager(self, obj):
        if obj.manager:
            return {"id": obj.manager.id, "full_name": obj.manager.full_name}
        return None


class UserDetailSerializer(UserListSerializer):
    direct_reports = serializers.SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ["direct_reports"]

    def get_direct_reports(self, obj):
        return [{"id": r.id, "full_name": r.full_name, "email": r.email}
                for r in obj.direct_reports.filter(is_active=True)]


class UserCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name  = serializers.CharField(max_length=255)
    email      = serializers.EmailField()
    phone      = serializers.CharField(max_length=30, required=False)
    password   = serializers.CharField(write_only=True, min_length=10)
    role_id    = serializers.IntegerField()
    sector_id  = serializers.IntegerField(required=False, allow_null=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name  = serializers.CharField(max_length=255, required=False)
    phone      = serializers.CharField(max_length=30,  required=False,
                                       allow_null=True)
    sector_id  = serializers.IntegerField(required=False, allow_null=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    role_id    = serializers.IntegerField(required=False)  # admin only
    is_active  = serializers.BooleanField(required=False)  # admin only


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=10)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserSession
        fields = ["id", "login_at", "logout_at", "ip_address", "is_active"]
