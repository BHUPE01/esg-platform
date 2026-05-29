"""
services.py — Normalization service.

Reads pending RawRecords and creates NormalizedRecords.
Can be run:
- per batch (after upload)
- on demand via API
"""
from django.db import transaction
from apps.ingestion.models import RawRecord
from apps.core.models import write_audit_log
from .models import NormalizedRecord
from .normalizers import normalize_raw_record


def normalize_batch(batch_id: int) -> dict:
    """
    Normalize all pending RawRecords in a batch.
    Returns a summary dict.
    """
    raw_records = RawRecord.objects.filter(
        batch_id=batch_id, status="pending"
    ).select_related("batch__organization")

    success, failed = 0, 0

    for raw in raw_records:
        try:
            normalize_single(raw)
            success += 1
        except Exception as e:
            raw.status = "failed"
            raw.error_message = str(e)
            raw.save(update_fields=["status", "error_message"])
            failed += 1

    return {"normalized": success, "failed": failed}


def normalize_single(raw_record: RawRecord) -> NormalizedRecord:
    """
    Normalize one RawRecord → create or update NormalizedRecord.
    """
    fields = normalize_raw_record(raw_record.source_type, raw_record.raw_data)

    with transaction.atomic():
        normalized, created = NormalizedRecord.objects.update_or_create(
            raw_record=raw_record,
            defaults={
                "organization": raw_record.organization,
                **fields,
            },
        )

        # Mark the raw record as normalized
        raw_record.status = "normalized"
        raw_record.save(update_fields=["status"])

    write_audit_log(
        organization=raw_record.organization,
        entity_type="NormalizedRecord",
        entity_id=normalized.id,
        action="normalized",
        new_value={
            "source_type": fields["source_type"],
            "warnings": fields.get("normalization_warnings", []),
        },
    )

    return normalized