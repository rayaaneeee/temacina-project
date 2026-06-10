from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.safex.models import TradeShow, Company, Document, Sector
from apps.safex.api.serializers import (
    TradeShowSerializer, CompanyListSerializer, CompanyDetailSerializer,
    DocumentSerializer, SectorSerializer,
)
from apps.safex.api.filters import CompanyFilter, DocumentFilter
from apps.safex.services.company import CompanyService
from apps.safex.services.trade_show import TradeShowService
from apps.safex.services.analytics import AnalyticsService
from apps.safex.services.search import SearchService

# ── Trade Shows ───────────────────────────────────────────────

class TradeShowListView(generics.ListAPIView):
    queryset = TradeShow.objects.all().order_by("-exhibition_year", "name")
    serializer_class = TradeShowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["exhibition_year", "country", "city"]
    search_fields = ["name", "city", "country"]
    ordering_fields = ["exhibition_year", "name"]

class TradeShowDetailView(generics.RetrieveAPIView):
    queryset = TradeShow.objects.all()
    serializer_class = TradeShowSerializer
    permission_classes = [IsAuthenticated]

class TradeShowStatsView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        stats = TradeShowService.get_trade_show_stats(pk)
        return Response(stats)

# ── Sectors ───────────────────────────────────────────────────

class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]

# ── Companies ─────────────────────────────────────────────────

class CompanyListView(generics.ListAPIView):
    serializer_class = CompanyListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ["legal_name", "normalized_legal_name"]
    ordering_fields = ["legal_name"]
    ordering = ["legal_name"]
    def filter_queryset(self, queryset):
        # Apply filter/search/ordering backends first, then deduplicate via subquery
        qs = super().filter_queryset(queryset)
        ids = qs.values_list("id", flat=True).distinct()
        ordering = qs.query.order_by or ["legal_name"]
        return (
            Company.objects
            .filter(id__in=ids)
            .prefetch_related("sectors", "addresses")
            .order_by(*ordering)
        )

    def get_queryset(self):
        return Company.objects.prefetch_related("sectors", "addresses")

class CompanyDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return (
            Company.objects
            .prefetch_related(
                "sectors", "addresses", "phones__phone_type",
                "emails", "websites", "social_networks__social_network_type",
                "contacts__phones__phone_type", "contacts__emails",
                "documents__trade_show",
            )
        )

class CompanyProfileCacheView(views.APIView):
    """Returns pre‑computed profile from cache (fastest endpoint)."""
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        profile = CompanyService.get_company_full_profile(pk)
        if not profile:
            return Response({"detail": "Not found."}, status=404)
        return Response(profile)

class CompanyPhonesView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        data = CompanyService.get_company_phones(pk)
        return Response(data)

class CompanyEmailsView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        data = CompanyService.get_company_emails(pk)
        return Response(data)

class CompanyCountPerTradeShowView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = CompanyService.get_company_count_per_trade_show()
        return Response(data)

# ── Documents ─────────────────────────────────────────────────

class DocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ["file_name"]
    ordering_fields = ["ingested_at", "page_count"]
    def get_queryset(self):
        return Document.objects.select_related("trade_show", "document_type").all()

class DocumentDetailView(generics.RetrieveAPIView):
    queryset = Document.objects.select_related("trade_show", "document_type")
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

class DocumentIngestionProgressView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        data = AnalyticsService.get_document_ingestion_progress(pk)
        return Response(data)

# ── Dashboard Analytics ───────────────────────────────────────

class DashboardKPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = AnalyticsService.get_dashboard_kpis()
        return Response(data)

# ── Global Search ─────────────────────────────────────────────

class GlobalSearchView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response({"detail": "Query must be at least 2 characters."}, status=400)
        results = SearchService.global_search(query)
        return Response(results)
