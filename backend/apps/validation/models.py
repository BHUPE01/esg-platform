from django.db import models
from apps.core.models import Organization
from apps.normalization.models import NormalizedRecord


class ValidationRule(models.Model):
    """
    A configurable rule that can be applied to normalized records.
    Rules are scoped to a source_type so we don't apply electricity
    rules to travel records.

    rule_type determines which validation function runs.
    parameters is a JSON config for that function (e.g. {"max_value": 10000}).
    """
    SEVERITY_CHOICES = [
        ("warning", "Warning"),
        ("error", "Error"),
    ]

    RULE_TYPE_CHOICES = [
        ("negative_quantity", "Negative Quantity"),
        ("quantity_threshold", "Quantity Above Threshold"),
        ("invalid_airport_code", "Invalid Airport Code"),
        ("unknown_unit", "Unknown Unit"),
        ("missing_required_field", "Missing Required Field"),
        ("invalid_date_range", "Invalid Date Range"),
        ("duplicate_meter_period", "Duplicate Meter + Period"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="validation_rules"
    )
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=100, choices=RULE_TYPE_CHOICES)
    source_type = models.CharField(max_length=50)   # which source this rule applies to
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="warning")
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.rule_type}) [{self.severity}]"


class ValidationFlag(models.Model):
    """
    A flag raised against a specific NormalizedRecord by a specific rule.
    Analysts review and resolve these.
    """
    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    normalized_record = models.ForeignKey(
        NormalizedRecord, on_delete=models.CASCADE, related_name="flags"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="validation_flags"
    )
    rule = models.ForeignKey(
        ValidationRule, on_delete=models.SET_NULL, null=True, related_name="flags"
    )
    rule_name = models.CharField(max_length=255)   # Snapshot in case rule is deleted
    severity = models.CharField(max_length=20)
    message = models.TextField()
    field_name = models.CharField(max_length=100, blank=True)  # Which field triggered it
    field_value = models.CharField(max_length=500, blank=True) # What the value was
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["normalized_record", "status"]),
        ]

    def __str__(self):
        return f"Flag [{self.severity}] on Record #{self.normalized_record_id}: {self.message[:60]}"