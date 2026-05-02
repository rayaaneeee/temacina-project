from rest_framework import generics, permissions
from apps.users.models import User
from apps.users.api.serializers import UserSerializer, UserUpdateSerializer
from apps.users.permissions import IsAdmin

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    search_fields  = ["email", "first_name", "last_name"]
    filterset_fields = ["role", "is_active"]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
