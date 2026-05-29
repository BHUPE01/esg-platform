"""
Run with: python manage.py shell < scripts/seed_data.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "esg_platform.settings")
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Organization, OrganizationMembership
from apps.ingestion.models import DataSource
from apps.validation.models import ValidationRule

# ── Organization ──────────────────────────────────────────────────────────────
org, _ = Organization.objects.get_or_create(
    slug="acme-corp",
    defaults={"name": "Acme Corporation"}
)
print(f"Org: {org}")

# ── Users ─────────────────────────────────────────────────────────────────────
admin_user = User.objects.filter(username="admin").first()
if not admin_user:
    admin_user = User.objects.create_superuser("admin", "admin@acme.com", "admin123")

analyst, _ = User.objects.get_or_create(
    username="analyst1",
    defaults={"email": "analyst@acme.com", "first_name": "Jane", "last_name": "Smith"}
)
analyst.set_password("analyst123")
analyst.save()

OrganizationMembership.objects.get_or_create(
    user=analyst, organization=org,
    defaults={"role": "analyst"}
)

# ── Data Sources ──────────────────────────────────────────────────────────────
sap_source, _ = DataSource.objects.get_or_create(
    organization=org, name="SAP Fuel Consumption",
    defaults={"source_type": "sap_csv", "description": "Monthly SAP fuel exports from ERP"}
)

utility_source, _ = DataSource.objects.get_or_create(
    organization=org, name="Electricity Meters",
    defaults={"source_type": "utility_csv", "description": "UK utility electricity billing data"}
)

travel_source, _ = DataSource.objects.get_or_create(
    organization=org, name="Travel API",
    defaults={"source_type": "travel_api", "description": "Concur-style travel data sync"}
)

print("Data sources created")

# ── Validation Rules ──────────────────────────────────────────────────────────
rules = [
    {
        "name": "No negative fuel quantity",
        "rule_type": "negative_quantity",
        "source_type": "sap_csv",
        "severity": "error",
        "parameters": {},
        "description": "Fuel quantity cannot be negative",
    },
    {
        "name": "Suspicious high fuel volume",
        "rule_type": "quantity_threshold",
        "source_type": "sap_csv",
        "severity": "warning",
        "parameters": {"max_value": 50000},
        "description": "Flag any fuel record above 50,000 liters for review",
    },
    {
        "name": "No negative electricity usage",
        "rule_type": "negative_quantity",
        "source_type": "utility_csv",
        "severity": "error",
        "parameters": {},
        "description": "kWh cannot be negative",
    },
    {
        "name": "Suspicious electricity usage",
        "rule_type": "quantity_threshold",
        "source_type": "utility_csv",
        "severity": "warning",
        "parameters": {"max_value": 100000},
        "description": "Flag kWh above 100,000 for review",
    },
    {
        "name": "Invalid airport code",
        "rule_type": "invalid_airport_code",
        "source_type": "travel_api",
        "severity": "error",
        "parameters": {},
        "description": "Airport codes must be valid IATA codes",
    },
    {
        "name": "Unknown fuel unit",
        "rule_type": "unknown_unit",
        "source_type": "sap_csv",
        "severity": "warning",
        "parameters": {},
        "description": "Flag records with unrecognized units of measure",
    },
    {
        "name": "Electricity billing date range",
        "rule_type": "invalid_date_range",
        "source_type": "utility_csv",
        "severity": "error",
        "parameters": {},
        "description": "billing_end must not be before billing_start",
    },
]

for rule_data in rules:
    ValidationRule.objects.get_or_create(
        organization=org,
        name=rule_data["name"],
        defaults=rule_data,
    )

print("Validation rules created")
print("\n✅ Seed complete!")
print("  Org:      Acme Corporation (id=1)")
print("  Admin:    admin / admin123")
print("  Analyst:  analyst1 / analyst123")
print(f"  SAP source id: {sap_source.id}")
print(f"  Utility source id: {utility_source.id}")
print(f"  Travel source id: {travel_source.id}")