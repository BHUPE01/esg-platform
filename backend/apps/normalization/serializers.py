from rest_framework import serializers
from .models import NormalizedRecord


class NormalizedRecordSerializer(serializers.ModelSerializer):
    raw_data = serializers.JSONField(source="raw_record.raw_data", read_only=True)
    row_number = serializers.IntegerField(source="raw_record.row_number", read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = [
            "id", "raw_record", "row_number", "raw_data",
            "source_type", "record_date",
            "quantity", "unit", "quantity_normalized", "unit_normalized",
            "site_code", "material_doc",
            "billing_start", "billing_end", "tariff",
            "traveler", "departure_airport", "arrival_airport",
            "cabin_class", "hotel_nights",
            "extra_data", "normalization_warnings",
            "review_status", "review_notes",
            "reviewed_by", "reviewed_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "raw_record", "row_number", "raw_data",
            "source_type", "created_at", "updated_at",
        ]