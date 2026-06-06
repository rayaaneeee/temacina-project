from django.db.models import Q
from apps.safex.models import Company, CompanyContact, Email, Phone


class SearchService:

    @staticmethod
    def global_search(query: str, limit: int = 20):
        """
        Searches companies by name, contacts by name,
        emails and phone numbers simultaneously.
        Returns a unified result dict.
        """
        companies = (
            Company.objects
            .filter(
                Q(legal_name__icontains=query) |
                Q(normalized_legal_name__icontains=query)
            )
            .values("id", "legal_name", "logo")[:limit]
        )
        contacts = (
            CompanyContact.objects
            .filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
            .select_related("company")
            .values("id", "first_name", "last_name", "role",
                    "company__id", "company__legal_name")[:limit]
        )
        emails = (
            Email.objects
            .filter(email_address__icontains=query)
            .values("id", "email_address", "is_professional")[:limit]
        )
        phones = (
            Phone.objects
            .filter(
                Q(full_phone_number__icontains=query) |
                Q(phone_number__icontains=query)
            )
            .select_related("phone_type")
            .values("id", "full_phone_number", "phone_type__label")[:limit]
        )
        return {
            "companies": list(companies),
            "contacts":  list(contacts),
            "emails":    list(emails),
            "phones":    list(phones),
        }
