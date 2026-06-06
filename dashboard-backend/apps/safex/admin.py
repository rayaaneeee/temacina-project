from django.contrib import admin
from apps.safex.models import (
    TradeShow, Sector, DocumentType, PhoneType, SocialNetworkType,
    Company, CompanyContact, CompanyAddress, CompanyDescription,
    Phone, Email, Website, SocialNetworkAccount,
    Document, CompanyProfileCache,
)


@admin.register(TradeShow)
class TradeShowAdmin(admin.ModelAdmin):
    list_display = ["name", "exhibition_year", "city", "country"]
    list_filter = ["exhibition_year", "country"]
    search_fields = ["name", "city"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "get_sectors", "get_country"]
    search_fields = ["legal_name", "normalized_legal_name"]
    list_filter = ["sectors"]

    def get_sectors(self, obj):
        return ", ".join(s.title for s in obj.sectors.all())
    get_sectors.short_description = "Sectors"

    def get_country(self, obj):
        addr = obj.addresses.first()
        return addr.country if addr else "—"
    get_country.short_description = "Country"


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "role", "company"]
    search_fields = ["first_name", "last_name", "role"]
    list_filter = ["role"]
    raw_id_fields = ["company"]


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ["full_phone_number", "phone_type", "country_dial_code"]
    list_filter = ["phone_type"]
    search_fields = ["phone_number", "full_phone_number"]


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ["email_address", "is_professional"]
    list_filter = ["is_professional"]
    search_fields = ["email_address"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["file_name", "trade_show", "document_type", "ingestion_status", "page_count", "ingested_at"]
    list_filter = ["ingestion_status", "document_type", "trade_show__exhibition_year"]
    search_fields = ["file_name"]
    date_hierarchy = "ingested_at"

# Lightweight registrations for lookup tables
admin.site.register(Sector)
admin.site.register(DocumentType)
admin.site.register(PhoneType)
admin.site.register(SocialNetworkType)
admin.site.register(Website)
admin.site.register(SocialNetworkAccount)
admin.site.register(CompanyAddress)
