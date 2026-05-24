from rest_framework import serializers
from apps.safex.models import (
    TradeShow, Sector, Company, CompanyContact,
    CompanyAddress, Phone, Email, Website,
    SocialNetworkAccount, Document, CompanyDescription,
)


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Sector
        fields = ["id", "title"]


class TradeShowSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TradeShow
        fields = ["id", "name", "exhibition_year", "venue_name", "city", "country"]


class PhoneSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="phone_type.label", read_only=True)

    class Meta:
        model  = Phone
        fields = ["id", "full_phone_number", "phone_number",
                  "country_dial_code", "type"]


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Email
        fields = ["id", "email_address", "is_professional"]


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Website
        fields = ["id", "url", "website_type", "description"]


class SocialNetworkAccountSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(source="social_network_type.code", read_only=True)

    class Meta:
        model  = SocialNetworkAccount
        fields = ["id", "platform", "account_value", "profile_url"]


class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CompanyAddress
        fields = ["id", "street", "postal_code", "city", "country"]


class CompanyContactSerializer(serializers.ModelSerializer):
    phones = PhoneSerializer(many=True, read_only=True)
    emails = EmailSerializer(many=True, read_only=True)

    class Meta:
        model  = CompanyContact
        fields = ["id", "first_name", "last_name", "role", "phones", "emails"]


class CompanyListSerializer(serializers.ModelSerializer):
    sectors = SectorSerializer(many=True, read_only=True)
    country = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = ["id", "legal_name", "logo", "sectors", "country"]

    def get_country(self, obj):
        addr = obj.addresses.first()
        return addr.country if addr else None


class CompanyDetailSerializer(serializers.ModelSerializer):
    sectors         = SectorSerializer(many=True, read_only=True)
    addresses       = CompanyAddressSerializer(many=True, read_only=True)
    phones          = PhoneSerializer(many=True, read_only=True)
    emails          = EmailSerializer(many=True, read_only=True)
    websites        = WebsiteSerializer(many=True, read_only=True)
    social_networks = SocialNetworkAccountSerializer(many=True, read_only=True)
    contacts        = CompanyContactSerializer(many=True, read_only=True)
    trade_shows     = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = [
            "id", "legal_name", "logo",
            "sectors", "addresses", "phones", "emails",
            "websites", "social_networks", "contacts", "trade_shows",
        ]

    def get_trade_shows(self, obj):
        return list({
            f"{d.trade_show.name} ({d.trade_show.exhibition_year})"
            for d in obj.documents.select_related("trade_show").all()
        })


class DocumentSerializer(serializers.ModelSerializer):
    trade_show    = TradeShowSerializer(read_only=True)
    document_type = serializers.CharField(source="document_type.label")

    class Meta:
        model  = Document
        fields = ["id", "trade_show", "document_type", "file_name",
                  "page_count", "ingestion_status", "ingested_at"]