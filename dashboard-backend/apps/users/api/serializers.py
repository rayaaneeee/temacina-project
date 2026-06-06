from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role",
                  "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["first_name", "last_name", "role"]
