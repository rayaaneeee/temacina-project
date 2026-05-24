from rest_framework import serializers
from apps.reports.models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['owner', 'status', 'file', 'error_msg']
