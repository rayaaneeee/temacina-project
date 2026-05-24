import os
import sys

# Set up Django
sys.path.append(r"c:\Users\belam\OneDrive\Bureau\1Program\temacina-project\dashboard-backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
django.setup()

from apps.safex.services.company import CompanyService

print("Testing get_companies_by_trade_show(1)...")
companies = CompanyService.get_companies_by_trade_show(1)[:5]
print(list(companies))

print("\nTesting get_companies_by_year(2024)...")
companies = CompanyService.get_companies_by_year(2024)[:5]
print(list(companies))

print("\nTesting get_company_full_profile for first company...")
first_company = CompanyService.get_companies_by_year(2024).first()
if first_company:
    print(CompanyService.get_company_full_profile(first_company.id))

print("\nTesting get_company_count_per_trade_show()...")
print(CompanyService.get_company_count_per_trade_show()[:5])
