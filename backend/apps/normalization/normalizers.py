"""
normalizers.py — Source-specific normalization logic.

Each normalizer takes a raw_data dict (straight from RawRecord.raw_data)
and returns a dict of clean fields for NormalizedRecord.

Key jobs:
- Map ugly column names to clean field names
- Parse messy dates to Python date objects
- Convert units to a standard base unit
- Collect warnings for suspicious-but-parseable values
"""
from datetime import date
from decimal import Decimal, InvalidOperation
from dateutil import parser as date_parser
from typing import Optional


# ─── Unit Conversion ──────────────────────────────────────────────────────────

UNIT_CONVERSION = {
    # Volume → Liters
    "l": ("L", Decimal("1")),
    "liter": ("L", Decimal("1")),
    "liters": ("L", Decimal("1")),
    "litre": ("L", Decimal("1")),
    "litres": ("L", Decimal("1")),
    "m3": ("m³", Decimal("1000")),          # 1 m³ = 1000 L
    "m³": ("m³", Decimal("1000")),
    "gallon": ("L", Decimal("3.78541")),
    "gal": ("L", Decimal("3.78541")),
    # Energy → kWh
    "kwh": ("kWh", Decimal("1")),
    "mwh": ("kWh", Decimal("1000")),        # 1 MWh = 1000 kWh
    "gj": ("kWh", Decimal("277.778")),      # 1 GJ = 277.778 kWh
    # Weight → kg
    "kg": ("kg", Decimal("1")),
    "t": ("kg", Decimal("1000")),           # metric tonne
    "tonne": ("kg", Decimal("1000")),
    "ton": ("kg", Decimal("1000")),
    "g": ("kg", Decimal("0.001")),
}


def normalize_unit(raw_unit: str, quantity: Decimal):
    """
    Returns (normalized_unit, normalized_quantity, warning_or_None).
    """
    key = raw_unit.strip().lower()
    if key in UNIT_CONVERSION:
        norm_unit, factor = UNIT_CONVERSION[key]
        return norm_unit, quantity * factor, None
    else:
        return raw_unit, quantity, f"Unknown unit '{raw_unit}' — not converted"


def parse_decimal(value: str) -> Optional[Decimal]:
    if not value:
        return None
    # Handle European number format: 1.234,56 → 1234.56
    cleaned = value.strip().replace(" ", "")
    if "," in cleaned and "." in cleaned:
        # European: 1.234,56
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return date_parser.parse(value, dayfirst=True).date()
    except Exception:
        return None


# ─── SAP Normalizer ───────────────────────────────────────────────────────────

# Known SAP column name aliases → clean field names
SAP_FIELD_MAP = {
    # Plant/site
    "WERKS": "site_code",
    "PLANT": "site_code",
    "WERK": "site_code",
    # Quantity
    "MENGE": "quantity",
    "QUANTITY": "quantity",
    "QTY": "quantity",
    # Unit
    "MEINS": "unit",
    "UOM": "unit",
    "UNIT": "unit",
    "BSTME": "unit",
    # Date
    "BUDAT": "record_date",
    "BLDAT": "record_date",
    "DATE": "record_date",
    "POSTING_DATE": "record_date",
    # Material doc
    "MBLNR": "material_doc",
    "MAT_DOC": "material_doc",
}


def normalize_sap(raw_data: dict) -> dict:
    warnings = []
    mapped = {}

    # Normalize column keys (upper-case, strip)
    for raw_key, value in raw_data.items():
        clean_key = SAP_FIELD_MAP.get(raw_key.upper().strip(), raw_key.lower())
        mapped[clean_key] = value

    # Parse quantity
    qty_raw = mapped.get("quantity", "")
    quantity = parse_decimal(qty_raw)
    if quantity is None and qty_raw:
        warnings.append(f"Could not parse quantity '{qty_raw}'")

    # Parse unit + convert
    unit_raw = mapped.get("unit", "")
    unit_normalized = unit_raw
    qty_normalized = quantity

    if quantity is not None and unit_raw:
        unit_normalized, qty_normalized, unit_warning = normalize_unit(unit_raw, quantity)
        if unit_warning:
            warnings.append(unit_warning)

    # Parse date
    date_raw = mapped.get("record_date", "")
    record_date = parse_date(date_raw)
    if record_date is None and date_raw:
        warnings.append(f"Could not parse date '{date_raw}'")

    # Collect unrecognized fields in extra_data
    known = {"site_code", "quantity", "unit", "record_date", "material_doc"}
    extra = {k: v for k, v in mapped.items() if k not in known}

    return {
        "source_type": "sap_csv",
        "site_code": mapped.get("site_code", ""),
        "quantity": quantity,
        "unit": unit_raw,
        "quantity_normalized": qty_normalized,
        "unit_normalized": unit_normalized,
        "record_date": record_date,
        "material_doc": mapped.get("material_doc", ""),
        "extra_data": extra,
        "normalization_warnings": warnings,
    }


# ─── Utility Normalizer ───────────────────────────────────────────────────────

def normalize_utility(raw_data: dict) -> dict:
    warnings = []

    # Field names are already clean for utility CSV
    meter_id = raw_data.get("meter_id", "").strip()
    kwh_raw = raw_data.get("kwh", "")
    tariff = raw_data.get("tariff", "").strip()
    billing_start_raw = raw_data.get("billing_start", "")
    billing_end_raw = raw_data.get("billing_end", "")

    quantity = parse_decimal(kwh_raw)
    if quantity is None and kwh_raw:
        warnings.append(f"Could not parse kwh '{kwh_raw}'")

    billing_start = parse_date(billing_start_raw)
    billing_end = parse_date(billing_end_raw)
    record_date = billing_start  # Use billing_start as the canonical date

    if billing_start is None and billing_start_raw:
        warnings.append(f"Could not parse billing_start '{billing_start_raw}'")
    if billing_end is None and billing_end_raw:
        warnings.append(f"Could not parse billing_end '{billing_end_raw}'")

    # Unit for utility is always kWh
    unit_normalized = "kWh"
    qty_normalized = quantity  # Already in kWh

    return {
        "source_type": "utility_csv",
        "site_code": meter_id,
        "quantity": quantity,
        "unit": "kWh",
        "quantity_normalized": qty_normalized,
        "unit_normalized": unit_normalized,
        "record_date": record_date,
        "billing_start": billing_start,
        "billing_end": billing_end,
        "tariff": tariff,
        "extra_data": {},
        "normalization_warnings": warnings,
    }


# ─── Travel Normalizer ────────────────────────────────────────────────────────

VALID_CABIN_CLASSES = {"economy", "premium_economy", "business", "first"}


def normalize_travel(raw_data: dict) -> dict:
    warnings = []

    traveler = raw_data.get("traveler", "").strip()
    dep = raw_data.get("departure_airport", "").strip().upper()
    arr = raw_data.get("arrival_airport", "").strip().upper()
    cabin = raw_data.get("cabin_class", "").strip().lower()
    hotel_nights_raw = raw_data.get("hotel_nights", "")
    date_raw = raw_data.get("travel_date", raw_data.get("date", ""))

    if cabin not in VALID_CABIN_CLASSES and cabin:
        warnings.append(f"Unrecognized cabin class '{cabin}'")

    hotel_nights = None
    if hotel_nights_raw != "":
        try:
            hotel_nights = int(str(hotel_nights_raw).strip())
        except (ValueError, TypeError):
            warnings.append(f"Could not parse hotel_nights '{hotel_nights_raw}'")

    record_date = parse_date(str(date_raw)) if date_raw else None

    return {
        "source_type": "travel_api",
        "traveler": traveler,
        "departure_airport": dep,
        "arrival_airport": arr,
        "cabin_class": cabin,
        "hotel_nights": hotel_nights,
        "record_date": record_date,
        "quantity": None,
        "unit": "",
        "quantity_normalized": None,
        "unit_normalized": "",
        "site_code": "",
        "extra_data": {k: v for k, v in raw_data.items()
                       if k not in {"traveler", "departure_airport",
                                    "arrival_airport", "cabin_class",
                                    "hotel_nights", "travel_date", "date"}},
        "normalization_warnings": warnings,
    }


# ─── Router ───────────────────────────────────────────────────────────────────

NORMALIZERS = {
    "sap_csv": normalize_sap,
    "utility_csv": normalize_utility,
    "travel_api": normalize_travel,
}


def normalize_raw_record(source_type: str, raw_data: dict) -> dict:
    normalizer = NORMALIZERS.get(source_type)
    if not normalizer:
        raise ValueError(f"No normalizer for source_type '{source_type}'")
    return normalizer(raw_data)