from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ReportSerializer
from apps.reports.models import Report
from apps.reports.tasks import generate_report

class ReportListCreateView(generics.ListCreateAPIView):
    serializer_class   = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        report = serializer.save(owner=self.request.user)
        generate_report.delay(str(report.id))   # async Celery task


class ReportDetailView(generics.RetrieveDestroyAPIView):
    serializer_class   = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(owner=self.request.user)
