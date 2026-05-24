from django.core.cache import cache
from django.db.models import Count, Prefetch, Q
from apps.safex.models import (
    Company, Phone, Email, Website,
    CompanyContact, CompanyAddress, SocialNetworkAccount,
    CompanyProfileCache,
)


def _distinct_companies(qs):
    """
    PostgreSQL cannot apply DISTINCT on rows containing 'json' columns.
    The companies table has a 'metadata' column of type json (not jsonb).
    Workaround: collect distinct IDs via .values_list, then re-query.
    """
    ids = (
        qs.order_by()          # drop any ordering before subquery
          .values_list("id", flat=True)
          .distinct()
    )
    return Company.objects.filter(id__in=ids)


class CompanyService:

    # ── 1. List companies filtered by trade show ──────────────
    @staticmethod
    def get_companies_by_trade_show(trade_show_id: int):
        """
        Returns all companies that appeared in documents
        belonging to the given trade show.
        """
        qs = Company.objects.filter(documents__trade_show_id=trade_show_id)
        return _distinct_companies(qs).order_by("legal_name")

    # ── 2. List companies filtered by year ────────────────────
    @staticmethod
    def get_companies_by_year(year: int):
        qs = Company.objects.filter(documents__trade_show__exhibition_year=year)
        return _distinct_companies(qs).order_by("legal_name")

    # ── 3. Filter by trade show AND year ─────────────────────
    @staticmethod
    def get_companies_by_show_and_year(trade_show_name: str, year: int):
        qs = Company.objects.filter(
            documents__trade_show__name=trade_show_name,
            documents__trade_show__exhibition_year=year,
        )
        return _distinct_companies(qs).order_by("legal_name")

    # ── 4. Filter by sector ───────────────────────────────────
    @staticmethod
    def get_companies_by_sector(sector_id: int):
        qs = Company.objects.filter(sectors__id=sector_id)
        return _distinct_companies(qs).order_by("legal_name")

    # ── 5. Filter by country ──────────────────────────────────
    @staticmethod
    def get_companies_by_country(country: str):
        qs = Company.objects.filter(addresses__country__iexact=country)
        return _distinct_companies(qs).order_by("legal_name")

    # ── 6. Combined filter (trade_show + year + sector + country)
    @staticmethod
    def get_companies_filtered(
        trade_show_id=None,
        year=None,
        sector_id=None,
        country=None,
        search=None,
    ):
        qs = Company.objects.all()

        if trade_show_id:
            qs = qs.filter(documents__trade_show_id=trade_show_id)
        if year:
            qs = qs.filter(documents__trade_show__exhibition_year=year)
        if sector_id:
            qs = qs.filter(sectors__id=sector_id)
        if country:
            qs = qs.filter(addresses__country__iexact=country)
        if search:
            qs = qs.filter(
                Q(legal_name__icontains=search) |
                Q(normalized_legal_name__icontains=search)
            )

        return _distinct_companies(qs).order_by("legal_name")

    # ── 7. Get all phone numbers for a company ────────────────
    @staticmethod
    def get_company_phones(company_id: int):
        """
        Returns company-level phones + all contact-level phones,
        annotated with phone type label.
        """
        company_phones = (
            Phone.objects
            .filter(companies__id=company_id)
            .select_related("phone_type")
            .values(
                "id",
                "full_phone_number",
                "phone_number",
                "country_dial_code",
                "phone_type__label",
            )
        )
        contact_phones = (
            Phone.objects
            .filter(contact_owners__company_id=company_id)
            .select_related("phone_type")
            .values(
                "id",
                "full_phone_number",
                "phone_number",
                "country_dial_code",
                "phone_type__label",
                "contact_owners__first_name",
                "contact_owners__last_name",
                "contact_owners__role",
            )
        )
        return {"company_phones": list(company_phones),
                "contact_phones": list(contact_phones)}

    # ── 8. Get all emails for a company ───────────────────────
    @staticmethod
    def get_company_emails(company_id: int):
        company_emails = (
            Email.objects
            .filter(companies__id=company_id)
            .values("id", "email_address", "is_professional")
        )
        contact_emails = (
            Email.objects
            .filter(contact_owners__company_id=company_id)
            .values(
                "id",
                "email_address",
                "is_professional",
                "contact_owners__first_name",
                "contact_owners__last_name",
                "contact_owners__role",
            )
        )
        return {"company_emails": list(company_emails),
                "contact_emails": list(contact_emails)}

    # ── 9. Full company profile (single DB query batch) ───────
    @staticmethod
    def get_company_full_profile(company_id: int):
        """
        Returns the complete profile of one company:
        addresses, contacts, phones, emails, websites,
        social networks, sectors, trade shows appeared in.
        Uses select_related + prefetch_related to avoid N+1.
        """
        cache_key = f"company:full_profile:{company_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            company = (
                Company.objects
                .prefetch_related(
                    "addresses",
                    Prefetch("phones", queryset=Phone.objects.select_related("phone_type")),
                    Prefetch("emails"),
                    Prefetch("websites"),
                    Prefetch(
                        "social_networks",
                        queryset=SocialNetworkAccount.objects.select_related("social_network_type"),
                    ),
                    Prefetch(
                        "contacts",
                        queryset=CompanyContact.objects.prefetch_related(
                            Prefetch("phones",
                                     queryset=Phone.objects.select_related("phone_type")),
                            "emails",
                        ),
                    ),
                    "sectors",
                    "documents__trade_show",
                )
                .get(id=company_id)
            )
        except Company.DoesNotExist:
            return None

        profile = _serialize_company_profile(company)
        cache.set(cache_key, profile, timeout=600)   # 10 min cache
        return profile

    # ── 10. Count companies per trade show (dashboard KPI) ───
    @staticmethod
    def get_company_count_per_trade_show():
        cache_key = "kpi:companies_per_trade_show"
        cached = cache.get(cache_key)
        if cached:
            return cached

        result = (
            Company.objects
            .values("documents__trade_show__name",
                    "documents__trade_show__exhibition_year")
            .annotate(company_count=Count("id", distinct=True))
            .order_by("-documents__trade_show__exhibition_year")
        )
        data = list(result)
        cache.set(cache_key, data, timeout=300)
        return data


def _serialize_company_profile(company: Company) -> dict:
    """Internal helper — converts ORM objects to plain dict for caching."""
    return {
        "id":         company.id,
        "legal_name": company.legal_name,
        "logo":       company.logo,
        "sectors":    [s.title for s in company.sectors.all()],
        "addresses":  [
            {"street": a.street, "city": a.city, "country": a.country,
             "postal_code": a.postal_code}
            for a in company.addresses.all()
        ],
        "phones":     [
            {"number": p.full_phone_number, "type": p.phone_type.label}
            for p in company.phones.all()
        ],
        "emails":     [
            {"address": e.email_address, "professional": e.is_professional}
            for e in company.emails.all()
        ],
        "websites":   [{"url": w.url, "type": w.website_type} for w in company.websites.all()],
        "social_networks": [
            {"platform": sn.social_network_type.code, "value": sn.account_value,
             "url": sn.profile_url}
            for sn in company.social_networks.all()
        ],
        "contacts":   [
            {
                "name":   f"{c.first_name} {c.last_name or ''}".strip(),
                "role":   c.role,
                "phones": [p.full_phone_number for p in c.phones.all()],
                "emails": [e.email_address for e in c.emails.all()],
            }
            for c in company.contacts.all()
        ],
        "trade_shows": list({
            f"{d.trade_show.name} ({d.trade_show.exhibition_year})"
            for d in company.documents.all()
        }),
    }
