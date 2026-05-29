from rest_framework import serializers
from .models import DataSource, UploadBatch, RawRecord


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ["id", "name", "source_type", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class UploadBatchSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source="data_source.name", read_only=True)
    uploaded_by_username = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )

    class Meta:
        model = UploadBatch
        fields = [
            "id", "data_source", "data_source_name", "uploaded_by_username",
            "original_filename", "status", "total_rows", "processed_rows",
            "failed_rows", "error_message", "created_at", "completed_at",
        ]
        read_only_fields = [
            "id", "status", "total_rows", "processed_rows",
            "failed_rows", "error_message", "created_at", "completed_at",
        ]


class UploadBatchCreateSerializer(serializers.Serializer):
    """
    Used only for the upload endpoint.
    We accept a file + data_source ID.
    """
    data_source_id = serializers.IntegerField()
    file = serializers.FileField()


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = [
            "id", "batch", "row_number", "raw_data",
            "source_type", "status", "error_message", "created_at",
        ]