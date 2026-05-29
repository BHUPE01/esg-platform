from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Organization


class DataSource(models.Model):
    """
    A named data source type: SAP, Utility, Travel API.
    Tells the ingestion pipeline which parser to use.
    """
    SOURCE_TYPES = [
        ("sap_csv", "SAP CSV Export"),
        ("utility_csv", "Utility Electricity CSV"),
        ("travel_api", "Mock Travel API"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="data_sources"
    )
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.organization.name} — {self.name} ({self.source_type})"


class UploadBatch(models.Model):
    """
    Represents one upload event.
    We store the original file and track the ingestion lifecycle.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="upload_batches"
    )
    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="upload_batches"
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="uploads"
    )
    original_file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Batch #{self.id} — {self.data_source.name} ({self.status})"


class RawRecord(models.Model):
    """
    One row from the original upload, stored exactly as-is.
    raw_data: the original CSV row as JSON (ugly column names and all).
    This is our source of truth — we never modify it.
    """
    STATUS_CHOICES = [
        ("pending", "Pending Normalization"),
        ("normalized", "Normalized"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
    ]

    batch = models.ForeignKey(
        UploadBatch, on_delete=models.CASCADE, related_name="raw_records"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="raw_records"
    )
    row_number = models.IntegerField()          # Line number in original file
    raw_data = models.JSONField()               # Original row, untouched
    source_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["batch", "row_number"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["batch", "row_number"]),
        ]

    def __str__(self):
        return f"RawRecord #{self.id} (Batch #{self.batch_id}, Row {self.row_number})"