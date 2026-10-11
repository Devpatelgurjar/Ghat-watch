"""Cleaning and normalization logic for water quality readings."""
import math
from typing import Optional, Tuple
from app.models import ReadingStatus

# Strings indicating missing data
MISSING_INDICATORS = {
    "",
    "_",
    "-",
    "*",
    "**",
    "not sampled",
    "none",
    "nan",
    "null",
}

# Strings indicating below detection limit
BDL_INDICATORS = {
    "bdl",
    "nd",
    "below detection limit",
    "not detected",
}


def classify_reading_status(
    value_raw: Optional[str],
    flag_raw: Optional[str],
    value_as_printed: Optional[str] = None
) -> Tuple[ReadingStatus, Optional[float]]:
    """
    Classify a raw reading into ReadingStatus and parsed numeric value (if any).

    Status rules:
    - numeric: has a valid parseable number
    - below_detection: BDL or ND in flag or printed text
    - missing: blank, '_', '-', '*', '**', 'not sampled'
    - no_table: handled when generating virtual rows for omitted report tables
    """
    flag_clean = (flag_raw or "").strip().lower()
    printed_clean = (value_as_printed or "").strip().lower()
    val_str = str(value_raw).strip() if value_raw is not None else ""

    # Check for Below Detection Limit first
    if flag_clean in BDL_INDICATORS or printed_clean in BDL_INDICATORS:
        return ReadingStatus.BELOW_DETECTION, None

    # Check for explicit missing indicators in flag or printed text
    if flag_clean in MISSING_INDICATORS and flag_clean != "":
        return ReadingStatus.MISSING, None

    if printed_clean in MISSING_INDICATORS and printed_clean != "":
        return ReadingStatus.MISSING, None

    # Check if value string is empty or invalid
    if not val_str or val_str.lower() in MISSING_INDICATORS:
        return ReadingStatus.MISSING, None

    # Attempt numeric parsing
    try:
        val_float = float(val_str)
        if math.isnan(val_float) or math.isinf(val_float):
            return ReadingStatus.MISSING, None
        return ReadingStatus.NUMERIC, val_float
    except (ValueError, TypeError):
        # If cannot parse, treat as missing
        return ReadingStatus.MISSING, None


def is_valid_reading(status: ReadingStatus) -> bool:
    """
    Check if a reading is considered valid.
    Valid readings = numeric or below_detection.
    Missing and no_table are NEVER valid.
    """
    return status in (ReadingStatus.NUMERIC, ReadingStatus.BELOW_DETECTION)
