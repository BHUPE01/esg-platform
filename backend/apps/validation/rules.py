"""
rules.py — Validation rule implementations.

Each rule function takes a NormalizedRecord and a parameters dict,
and returns a list of (field_name, field_value, message) tuples.
An empty list means the record passed the rule.
"""
from decimal import Decimal
from typing import Optional

# IATA 3-letter airport codes — a representative subset for demo
# In production you'd load this from a database or official IATA feed
KNOWN_AIRPORT_CODES = {
    "JFK", "LHR", "CDG", "DXB", "SIN", "HND", "LAX", "ORD", "ATL",
    "FRA", "AMS", "ICN", "PEK", "SYD", "GRU", "DEL", "BOM", "MUC",
    "YYZ", "NRT", "BCN", "MAD", "FCO", "ZRH", "CPH", "OSL", "ARN",
    "HEL", "VIE", "BRU", "LIS", "DUB", "MAN", "STN", "LGW", "BHX",
    "EDI", "GVA", "MXP", "LIN", "HAM", "BER", "DUS", "STR", "CGN",
    "MEX", "GIG", "EZE", "BOG", "SCL", "LIM", "UIO", "CCS", "MIA",
    "SFO", "SEA", "BOS", "DFW", "DEN", "PHX", "LAS", "MCO", "IAH",
    "BLR", "HYD", "MAA", "CCU", "AMD", "PNQ", "GOI", "COK", "TRV",
}

KNOWN_UNITS = {
    "l", "liter", "liters", "litre", "litres",
    "m3", "m³", "gallon", "gal",
    "kwh", "mwh", "gj",
    "kg", "t", "tonne", "ton", "g",
}


def check_negative_quantity(record, params: dict) -> list:
    if record.quantity is not None and record.quantity < 0:
        return [("quantity", str(record.quantity), "Quantity is negative")]
    return []


def check_quantity_threshold(record, params: dict) -> list:
    max_value = Decimal(str(params.get("max_value", 9999999)))
    if record.quantity is not None and record.quantity > max_value:
        return [(
            "quantity",
            str(record.quantity),
            f"Quantity {record.quantity} exceeds threshold {max_value}"
        )]
    return []


def check_invalid_airport_code(record, params: dict) -> list:
    flags = []
    for field in ("departure_airport", "arrival_airport"):
        code = getattr(record, field, "").upper()
        if code and code not in KNOWN_AIRPORT_CODES:
            flags.append((field, code, f"Unrecognized IATA airport code '{code}'"))
    return flags


def check_unknown_unit(record, params: dict) -> list:
    unit = (record.unit or "").strip().lower()
    if unit and unit not in KNOWN_UNITS:
        return [("unit", record.unit, f"Unknown unit '{record.unit}'")]
    return []


def check_missing_required_field(record, params: dict) -> list:
    required_fields = params.get("fields", [])
    flags = []
    for field in required_fields:
        value = getattr(record, field, None)
        if value is None or str(value).strip() == "":
            flags.append((field, "", f"Required field '{field}' is missing or empty"))
    return flags


def check_invalid_date_range(record, params: dict) -> list:
    if record.billing_start and record.billing_end:
        if record.billing_end < record.billing_start:
            return [(
                "billing_end",
                str(record.billing_end),
                f"billing_end ({record.billing_end}) is before billing_start ({record.billing_start})"
            )]
    return []


def check_duplicate_meter_period(record, params: dict) -> list:
    """
    Check if another NormalizedRecord has same site_code + billing_start + billing_end.
    """
    from apps.normalization.models import NormalizedRecord
    if not record.site_code or not record.billing_start:
        return []
    dup = NormalizedRecord.objects.filter(
        organization=record.organization,
        source_type="utility_csv",
        site_code=record.site_code,
        billing_start=record.billing_start,
        billing_end=record.billing_end,
    ).exclude(id=record.id).exists()

    if dup:
        return [(
            "site_code",
            record.site_code,
            f"Duplicate meter '{record.site_code}' for period {record.billing_start}–{record.billing_end}"
        )]
    return []


RULE_FUNCTIONS = {
    "negative_quantity": check_negative_quantity,
    "quantity_threshold": check_quantity_threshold,
    "invalid_airport_code": check_invalid_airport_code,
    "unknown_unit": check_unknown_unit,
    "missing_required_field": check_missing_required_field,
    "invalid_date_range": check_invalid_date_range,
    "duplicate_meter_period": check_duplicate_meter_period,
}