from django.db import models
from apps.core.models import Organization
from apps.ingestion.models import RawRecord


class NormalizedRecord(models.Model):
    """
    A cleaned, standardized version of a RawRecord.

    All source types map into this common schema:
    - quantity + unit (with unit always normalized to SI)
    - date fields parsed to proper date
    - source-specific metadata in extra_data

    review_status drives the analyst workflow.
    """
    REVIEW_STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("flagged", "Flagged for Review"),
    ]

    SOURCE_TYPES = [
        ("sap_csv", "SAP CSV"),
        ("utility_csv", "Utility CSV"),
        ("travel_api", "Travel API"),
    ]

    # Traceability
    raw_record = models.OneToOneField(
        RawRecord, on_delete=models.CASCADE, related_name="normalized"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="normalized_records"
    )

    # Common schema fields
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    record_date = models.DateField(null=True, blank=True)

    # Energy / quantity
    quantity = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)  # Always normalized (kWh, L, m3, etc.)
    quantity_normalized = models.DecimalField(  # Always in SI base unit
        max_digits=15, decimal_places=4, null=True, blank=True
    )
    unit_normalized = models.CharField(max_length=20, blank=True)

    # Location / identifiers
    site_code = models.CharField(max_length=100, blank=True)   # plant / meter_id
    
    # SAP-specific
    material_doc = models.CharField(max_length=100, blank=True)

    # Utility-specific
    billing_start = models.DateField(null=True, blank=True)
    billing_end = models.DateField(null=True, blank=True)
    tariff = models.CharField(max_length=100, blank=True)

    # Travel-specific
    traveler = models.CharField(max_length=255, blank=True)
    departure_airport = models.CharField(max_length=10, blank=True)
    arrival_airport = models.CharField(max_length=10, blank=True)
    cabin_class = models.CharField(max_length=50, blank=True)
    hotel_nights = models.IntegerField(null=True, blank=True)

    # Overflow — any source-specific fields that don't fit above
    extra_data = models.JSONField(default=dict, blank=True)

    # Workflow
    review_status = models.CharField(
        max_length=20, choices=REVIEW_STATUS_CHOICES, default="pending"
    )
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reviewed_records"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Normalization metadata
    normalization_warnings = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "review_status"]),
            models.Index(fields=["source_type", "record_date"]),
            models.Index(fields=["organization", "source_type"]),
        ]

    def __str__(self):
        return f"NormalizedRecord #{self.id} ({self.source_type}, {self.review_status})"