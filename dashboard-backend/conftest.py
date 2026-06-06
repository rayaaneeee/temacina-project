import pytest
from django.db import connection

SAFEX_MODELS = [
    "trade_shows", "sectors", "document_types", "phone_types",
    "social_network_types", "languages", "companies",
    "company_contacts", "company_addresses", "company_descriptions",
    "phones", "emails", "websites", "social_network_accounts",
    "documents", "document_languages", "trade_show_sectors",
    "company_sectors", "company_docs", "company_phones",
    "company_contact_phones", "company_emails", "company_contact_emails",
    "company_websites", "company_social_networks",
    "company_contact_social_networks", "company_profile_cache",
    "phone_origin_docs", "address_origin_docs", "website_origin_docs",
    "email_origin_docs", "contact_origin_docs", "social_network_origin_docs",
]

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Create all managed=False tables in the test DB before any test runs.
    Uses Django's schema editor so column types match the ORM exactly.
    """
    from django.apps import apps
    with django_db_blocker.unblock():
        with connection.schema_editor() as editor:
            for model in apps.get_app_config("safex").get_models():
                try:
                    editor.create_model(model)
                except Exception:
                    pass   # table may already exist; ignore
