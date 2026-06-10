from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.models import User, Role, UserSector, UserSession
from apps.users.permissions import (
    IsAdminOrAbove, IsManagerOrAbove, IsSuperAdmin, CanManageUser
)
from apps.users.api.serializers import (
    UserListSerializer, UserDetailSerializer,
    UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, UserSectorSerializer, UserSessionSerializer,
)
from apps.users.services.user import UserService
from apps.audit.services import write_log


class MeView(views.APIView):
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        s = UserUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        # Self-update: only non-privileged fields
        allowed = {"first_name", "last_name", "phone"}
        data    = {k: v for k, v in s.validated_data.items() if k in allowed}
        user    = UserService.update_user(request.user, request.user, data)
        return Response(UserDetailSerializer(user).data)


class UserListCreateView(views.APIView):
    permission_classes = [IsAdminOrAbove]

    def get(self, request):
        filters = {
            "role":       request.query_params.get("role"),
            "sector_id":  request.query_params.get("sector_id"),
            "manager_id": request.query_params.get("manager_id"),
        }
        users = UserService.get_all({k: v for k, v in filters.items() if v})
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        s = UserCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            user = UserService.create_user(request.user, s.validated_data)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(UserDetailSerializer(user).data,
                        status=status.HTTP_201_CREATED)


class UserDetailView(views.APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request, pk):
        user = UserService.get_by_id(pk)
        if not user:
            return Response({"detail": "Not found."}, status=404)
        return Response(UserDetailSerializer(user).data)

    def patch(self, request, pk):
        target = UserService.get_by_id(pk)
        if not target:
            return Response({"detail": "Not found."}, status=404)
        s = UserUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            user = UserService.update_user(request.user, target, s.validated_data)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=403)
        return Response(UserDetailSerializer(user).data)

    def delete(self, request, pk):
        target = UserService.get_by_id(pk)
        if not target:
            return Response({"detail": "Not found."}, status=404)
        try:
            UserService.deactivate_user(request.user, target)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=403)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangeRoleView(views.APIView):
    permission_classes = [IsAdminOrAbove]

    def post(self, request, pk):
        target   = UserService.get_by_id(pk)
        new_role = request.data.get("role")
        if not target or not new_role:
            return Response({"detail": "Invalid request."}, status=400)
        try:
            UserService.change_role(request.user, target, new_role)
        except (PermissionError, Role.DoesNotExist) as e:
            return Response({"detail": str(e)}, status=403)
        return Response({"detail": f"Role changed to {new_role}."})


class AssignCompanyView(views.APIView):
    permission_classes = [IsAdminOrAbove]

    def post(self, request, pk):
        target     = UserService.get_by_id(pk)
        company_id = request.data.get("company_id")
        if not target or not company_id:
            return Response({"detail": "Invalid request."}, status=400)
        try:
            obj = UserService.assign_company(target, int(company_id), request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": "Company assigned.", "id": obj.id},
                        status=201)


class UserAssignedCompaniesView(views.APIView):
    def get(self, request, pk):
        from apps.safex.api.serializers import CompanyListSerializer
        target    = UserService.get_by_id(pk)
        if not target:
            return Response({"detail": "Not found."}, status=404)
        companies = UserService.get_assigned_companies(target)
        write_log(
            user=request.user, action="COMPANY_VIEWED",
            entity_type="User", entity_id=target.id, details=None,
        )
        return Response(CompanyListSerializer(companies, many=True).data)


class DirectReportsView(views.APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request, pk):
        reports = UserService.get_direct_reports(pk)
        return Response(UserListSerializer(reports, many=True).data)


class UserSessionsView(views.APIView):
    permission_classes = [IsAdminOrAbove]

    def get(self, request, pk):
        sessions = UserSession.objects.filter(
            user_id=pk
        ).order_by("-login_at")[:50]
        return Response(UserSessionSerializer(sessions, many=True).data)


class RoleListView(generics.ListAPIView):
    queryset           = Role.objects.all()
    serializer_class   = RoleSerializer
    permission_classes = [IsAdminOrAbove]


class UserSectorListView(generics.ListAPIView):
    queryset           = UserSector.objects.all()
    serializer_class   = UserSectorSerializer
    permission_classes = [IsAuthenticated]
