import os, sys
sys.path.insert(0, ".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check what schemas exist
cursor.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
print("=== All schemas ===")
for row in cursor.fetchall():
    print(row)

# Check where tables are
cursor.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_name IN ('companies', 'trade_shows', 'sectors', 'documents', 'company_docs')
    ORDER BY table_schema, table_name
""")
print("\n=== Table locations ===")
for row in cursor.fetchall():
    print(row)

# Count companies directly
cursor.execute("SELECT count(*) FROM companies")
print(f"\n=== Companies count (no schema) === {cursor.fetchone()}")

# Try with schema
try:
    cursor.execute('SELECT count(*) FROM "Safex2022_2030".companies')
    print(f"=== Companies count (Safex2022_2030 schema) === {cursor.fetchone()}")
except Exception as e:
    print(f"=== Error with schema: {e}")
