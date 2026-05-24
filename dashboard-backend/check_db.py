import os, sys
sys.path.insert(0, ".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check column types for companies table
cursor.execute("""
    SELECT column_name, data_type, udt_name
    FROM information_schema.columns
    WHERE table_name = 'companies'
    ORDER BY ordinal_position
""")
print("=== companies table columns ===")
for row in cursor.fetchall():
    print(row)

# Also check the search_path / schema
cursor.execute("SHOW search_path")
print("\n=== search_path ===")
print(cursor.fetchone())
