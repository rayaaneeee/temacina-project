from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework import status
from django.db import transaction, connection
from apps.safex.models import (
    TradeShow, Company, Document, Sector, CompanyContact,
    CompanyAddress, Phone, PhoneType, Email, Website,
    CompanyPhone, CompanyEmail, CompanyWebsite, CompanySector,
)
from apps.safex.api.serializers import (
    TradeShowSerializer, CompanyListSerializer, CompanyDetailSerializer,
    CompanyWriteSerializer, ContactListSerializer,
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

class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return CompanyWriteSerializer
        return CompanyDetailSerializer

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

    def _require_admin(self, request):
        role = getattr(request.user, "role", None)
        role_name = role.name if hasattr(role, "name") else str(role or "")
        if role_name not in ("admin", "superadmin"):
            return Response(
                {"detail": "Only admins can modify companies."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def update(self, request, *args, **kwargs):
        err = self._require_admin(request)
        if err:
            return err
        company = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            # 1. Scalar fields
            if "legal_name" in data:
                company.legal_name = data["legal_name"]
            if "logo" in data:
                company.logo = data["logo"]
            company.save()

            # 2. Address (update first, or create)
            if "address" in data and data["address"] is not None:
                addr_data = data["address"]
                addr = company.addresses.first()
                if addr:
                    for field in ("street", "city", "country", "postal_code"):
                        if field in addr_data:
                            setattr(addr, field, addr_data[field])
                    addr.save()
                else:
                    CompanyAddress.objects.create(company=company, **{
                        k: v for k, v in addr_data.items()
                        if k in ("street", "city", "country", "postal_code")
                    })

            # Helper: raw delete on junction tables that have no surrogate PK
            def raw_delete(table, company_id):
                with connection.cursor() as cur:
                    cur.execute(f"DELETE FROM {table} WHERE company_id = %s", [company_id])

            # 3. Phones — replace entire list
            if "phones" in data and data["phones"] is not None:
                default_type = PhoneType.objects.get(code="FIX")
                raw_delete("company_phones", company.pk)
                for num in data["phones"]:
                    num = num.strip()
                    if not num:
                        continue
                    phone, _ = Phone.objects.get_or_create(
                        full_phone_number=num,
                        defaults={"phone_number": num, "phone_type": default_type}
                    )
                    with connection.cursor() as cur:
                        cur.execute(
                            "INSERT INTO company_phones (company_id, phone_id) "
                            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                            [company.pk, phone.pk]
                        )

            # 4. Emails — replace entire list
            if "emails" in data and data["emails"] is not None:
                raw_delete("company_emails", company.pk)
                for addr_str in data["emails"]:
                    addr_str = addr_str.strip().lower()
                    if not addr_str:
                        continue
                    email_obj, _ = Email.objects.get_or_create(
                        email_address=addr_str,
                        defaults={"is_professional": True}
                    )
                    with connection.cursor() as cur:
                        cur.execute(
                            "INSERT INTO company_emails (company_id, email_id) "
                            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                            [company.pk, email_obj.pk]
                        )

            # 5. Website — replace all
            if "website" in data:
                url = (data["website"] or "").strip()
                raw_delete("company_websites", company.pk)
                if url:
                    website_obj, _ = Website.objects.get_or_create(url=url)
                    with connection.cursor() as cur:
                        cur.execute(
                            "INSERT INTO company_websites (company_id, website_id) "
                            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                            [company.pk, website_obj.pk]
                        )

            # 6. Sectors — replace assignments
            if "sector_ids" in data and data["sector_ids"] is not None:
                raw_delete("company_sectors", company.pk)
                for sid in data["sector_ids"]:
                    try:
                        sector = Sector.objects.get(pk=sid)
                        with connection.cursor() as cur:
                            cur.execute(
                                "INSERT INTO company_sectors (company_id, sector_id) "
                                "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                [company.pk, sector.pk]
                            )
                    except Sector.DoesNotExist:
                        pass

        # Return updated detail
        company.refresh_from_db()
        out = CompanyDetailSerializer(
            Company.objects.prefetch_related(
                "sectors", "addresses", "phones__phone_type",
                "emails", "websites", "social_networks__social_network_type",
                "contacts__phones__phone_type", "contacts__emails",
                "documents__trade_show",
            ).get(pk=company.pk)
        )
        return Response(out.data)

    def destroy(self, request, *args, **kwargs):
        err = self._require_admin(request)
        if err:
            return err
        return super().destroy(request, *args, **kwargs)


class ContactListView(generics.ListAPIView):
    """All person contacts across all companies."""
    serializer_class = ContactListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name", "role", "company__legal_name"]

    def get_queryset(self):
        return (
            CompanyContact.objects
            .select_related("company")
            .prefetch_related("phones__phone_type", "emails")
            .order_by("company__legal_name", "last_name")
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
