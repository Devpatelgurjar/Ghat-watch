"""Configuration settings for Ghat Watch backend."""
from pathlib import Path
from typing import Dict, List, Tuple

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "resources"

# Data file paths
CSV_FILE = DATA_DIR / "bhopal_ghats_2023_2025.csv"
CRITERIA_FILE = DATA_DIR / "cpcb_water_quality_criteria.csv"

# Report filename mapping by year
REPORT_FILES_BY_YEAR: Dict[int, str] = {
    2025: "Ganesh_and_Durga_visarjan_report-2025.pdf",
    2024: "Ganesh_and_Durga_visarjan_report-2024.pdf",
    2023: "Idol_immer._Report_23_CPCB.pdf",
}

# The 7 authoritative Bhopal ghat sites
AUTHORITATIVE_SITES: List[str] = [
    "Bairagarh (Sant Hirdaram) kund",
    "Hathaikheda dam / kund",
    "Khatlapura ghat",
    "Malikhedi kund",
    "Prempura ghat",
    "Rani Kamlapati ghat / Kamla Park kund",
    "Shahpura lake ghat",
]

# Lake mappings
SITE_WATER_BODIES: Dict[str, str] = {
    "Bairagarh (Sant Hirdaram) kund": "Upper Lake",
    "Hathaikheda dam / kund": "Hathaikheda dam",
    "Khatlapura ghat": "Lower Lake",
    "Malikhedi kund": "Kund",
    "Prempura ghat": "Upper Lake",
    "Rani Kamlapati ghat / Kamla Park kund": "Lower Lake",
    "Shahpura lake ghat": "Shahpura Lake",
}

# Expected festival-year combinations across 2023-2025
EXPECTED_FESTIVAL_YEARS: List[Tuple[int, str]] = [
    (2023, "Ganesh"),
    (2023, "Durga"),
    (2024, "Ganesh"),
    (2024, "Durga"),
    (2025, "Ganesh"),
    (2025, "Durga"),
]

EXPECTED_PHASES: List[str] = ["pre", "during", "after"]

# Scored parameters vs unscored parameters
SCORED_PARAMETERS: List[str] = [
    "Dissolved oxygen",
    "BOD",
    "pH",
]

UNSCORED_PARAMETERS: List[str] = [
    "COD",
    "Conductivity",
    "Dissolved solids",
    "Suspended solids",
    "Total solids",
    "Turbidity",
    "Chromium",
    "Copper",
    "Lead",
    "Zinc",
]

# Expected scored count per ghat = 6 festival-years * 3 phases * 3 scored parameters = 54
EXPECTED_SCORED_COUNT_PER_GHAT: int = len(EXPECTED_FESTIVAL_YEARS) * len(EXPECTED_PHASES) * len(SCORED_PARAMETERS)

# Festival weightings: Durga readings weight 1.5, Ganesh 1.0 (upcoming event is Durga)
FESTIVAL_WEIGHTS: Dict[str, float] = {
    "Durga": 1.5,
    "Ganesh": 1.0,
}

# Baseline scoring weights (total 100)
BASE_SCORING_WEIGHTS: Dict[str, float] = {
    "do_failure_rate": 35.0,
    "bod_failure_rate": 25.0,
    "worst_severity": 10.0,
    "ph_failure_rate": 5.0,
    "immersion_impact": 15.0,
    "no_recovery": 10.0,
}

# 3 Alternative weighting schemes for sensitivity checks
SENSITIVITY_WEIGHT_SCHEMES: Dict[str, Dict[str, float]] = {
    "dissolved_oxygen_priority": {
        "do_failure_rate": 45.0,
        "bod_failure_rate": 20.0,
        "worst_severity": 10.0,
        "ph_failure_rate": 5.0,
        "immersion_impact": 10.0,
        "no_recovery": 10.0,
    },
    "impact_and_recovery_priority": {
        "do_failure_rate": 25.0,
        "bod_failure_rate": 20.0,
        "worst_severity": 10.0,
        "ph_failure_rate": 5.0,
        "immersion_impact": 25.0,
        "no_recovery": 15.0,
    },
    "severity_and_equal_failure": {
        "do_failure_rate": 30.0,
        "bod_failure_rate": 30.0,
        "worst_severity": 20.0,
        "ph_failure_rate": 10.0,
        "immersion_impact": 5.0,
        "no_recovery": 5.0,
    },
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.80,    # >= 80%
    "medium": 0.50,  # 50% to 79%
}

# CPCB Class B (outdoor bathing) limits
CLASS_B_LIMITS = {
    "Dissolved oxygen": {"type": "min", "value": 5.0, "unit": "mg/l"},
    "BOD": {"type": "max", "value": 3.0, "unit": "mg/l"},
    "pH": {"type": "range", "min": 6.5, "max": 8.5, "unit": ""},
}
