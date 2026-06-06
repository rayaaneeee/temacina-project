import django_filters
from apps.safex.models import Company, Document

class CompanyFilter(django_filters.FilterSet):
    trade_show_id  = django_filters.NumberFilter(field_name="documents__trade_show__id")
    year           = django_filters.NumberFilter(field_name="documents__trade_show__exhibition_year")
    trade_show_name = django_filters.CharFilter(field_name="documents__trade_show__name", lookup_expr="icontains")
    sector_id      = django_filters.NumberFilter(field_name="sectors__id")
    sector_title   = django_filters.CharFilter(field_name="sectors__title", lookup_expr="icontains")
    country        = django_filters.CharFilter(field_name="addresses__country", lookup_expr="iexact")
    city           = django_filters.CharFilter(field_name="addresses__city", lookup_expr="icontains")
    name           = django_filters.CharFilter(field_name="legal_name", lookup_expr="icontains")

    class Meta:
        model = Company
        fields = ["trade_show_id", "year", "sector_id", "country", "city", "name"]

class DocumentFilter(django_filters.FilterSet):
    trade_show_id = django_filters.NumberFilter(field_name="trade_show__id")
    year          = django_filters.NumberFilter(field_name="trade_show__exhibition_year")
    status        = django_filters.CharFilter(field_name="ingestion_status")
    doc_type      = django_filters.CharFilter(field_name="document_type__code")

    class Meta:
        model = Document
        fields = ["trade_show_id", "year", "status", "doc_type"]
