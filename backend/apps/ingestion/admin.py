from django.contrib import admin
from .models import DataSource, UploadBatch, RawRecord


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "source_type", "organization", "is_active"]
    list_filter = ["source_type", "organization"]


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ["id", "data_source", "status", "total_rows", "created_at"]
    list_filter = ["status", "data_source__source_type"]
    readonly_fields = ["created_at", "completed_at"]


@admin.register(RawRecord)
class RawRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "batch", "row_number", "source_type", "status"]
    list_filter = ["source_type", "status"]
    readonly_fields = ["raw_data", "created_at"]