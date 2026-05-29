"""
services.py — Validation service.

Runs all active rules for an organization against a NormalizedRecord
or a full batch.
"""
from apps.normalization.models import NormalizedRecord
from apps.core.models import write_audit_log
from .models import ValidationRule, ValidationFlag
from .rules import RULE_FUNCTIONS


def validate_record(normalized_record: NormalizedRecord) -> list:
    """
    Run all active rules that match this record's source_type.
    Creates ValidationFlag objects for any failures.
    Returns list of created flags.
    """
    rules = ValidationRule.objects.filter(
        organization=normalized_record.organization,
        source_type=normalized_record.source_type,
        is_active=True,
    )

    created_flags = []

    for rule in rules:
        fn = RULE_FUNCTIONS.get(rule.rule_type)
        if not fn:
            continue

        violations = fn(normalized_record, rule.parameters)

        for field_name, field_value, message in violations:
            flag = ValidationFlag.objects.create(
                normalized_record=normalized_record,
                organization=normalized_record.organization,
                rule=rule,
                rule_name=rule.name,
                severity=rule.severity,
                message=message,
                field_name=field_name,
                field_value=str(field_value),
                status="open",
            )
            created_flags.append(flag)

    # If flags were raised, update review_status to flagged
    if created_flags:
        error_flags = [f for f in created_flags if f.severity == "error"]
        if error_flags:
            normalized_record.review_status = "flagged"
            normalized_record.save(update_fields=["review_status"])

        write_audit_log(
            organization=normalized_record.organization,
            entity_type="NormalizedRecord",
            entity_id=normalized_record.id,
            action="flagged",
            new_value={"flags": [f.message for f in created_flags]},
        )

    return created_flags


def validate_batch(batch_id: int) -> dict:
    """
    Run validation on all NormalizedRecords linked to a batch.
    """
    records = NormalizedRecord.objects.filter(
        raw_record__batch_id=batch_id
    )

    total_flags = 0
    for record in records:
        flags = validate_record(record)
        total_flags += len(flags)

    return {"records_validated": records.count(), "flags_raised": total_flags}