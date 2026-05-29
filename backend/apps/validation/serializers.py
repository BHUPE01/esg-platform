from rest_framework import serializers
from .models import ValidationRule, ValidationFlag


class ValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRule
        fields = [
            "id", "name", "rule_type", "source_type",
            "severity", "parameters", "is_active", "description",
        ]


class ValidationFlagSerializer(serializers.ModelSerializer):
    normalized_record_id = serializers.IntegerField(
        source="normalized_record.id", read_only=True
    )

    class Meta:
        model = ValidationFlag
        fields = [
            "id", "normalized_record_id", "rule_name", "severity",
            "message", "field_name", "field_value",
            "status", "resolution_notes", "created_at",
        ]