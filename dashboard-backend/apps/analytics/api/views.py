from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.analytics.services import AnalyticsService

class DashboardMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.get_dashboard_metrics(request.user)
        return Response(data)
