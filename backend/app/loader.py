"""CSV Data loader and parser for Bhopal Ghats water quality records."""
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.config import (
    AUTHORITATIVE_SITES,
    CSV_FILE,
    EXPECTED_FESTIVAL_YEARS,
    EXPECTED_PHASES,
    REPORT_FILES_BY_YEAR,
    SCORED_PARAMETERS,
    SITE_WATER_BODIES,
)
from app.cleaning import classify_reading_status
from app.limits import evaluate_reading_against_limits
from app.models import LimitEvaluation, ReadingRecord, ReadingStatus

# Slug mapping for URL-safe ghat identifiers
SITE_TO_ID: Dict[str, str] = {
    "Bairagarh (Sant Hirdaram) kund": "bairagarh",
    "Hathaikheda dam / kund": "hathaikheda",
    "Khatlapura ghat": "khatlapura",
    "Malikhedi kund": "malikhedi",
    "Prempura ghat": "prempura",
    "Rani Kamlapati ghat / Kamla Park kund": "rani-kamlapati",
    "Shahpura lake ghat": "shahpura",
}

ID_TO_SITE: Dict[str, str] = {v: k for k, v in SITE_TO_ID.items()}


def get_site_id(site_name: str) -> str:
    """Return URL-safe ID for a given site name."""
    if site_name in SITE_TO_ID:
        return SITE_TO_ID[site_name]
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", site_name.lower()).strip("-")
    return slug


def get_site_by_id(site_id: str) -> Optional[str]:
    """Return canonical site name for a given site ID."""
    return ID_TO_SITE.get(site_id)


class DataLoader:
    """In-memory data store for Bhopal water quality records."""

    def __init__(self, csv_path: Path = CSV_FILE):
        self.csv_path = csv_path
        self._records: List[ReadingRecord] = []
        self._records_by_site: Dict[str, List[ReadingRecord]] = {}
        self._loaded = False

    def load(self) -> List[ReadingRecord]:
        """Load, parse, clean, and evaluate all readings from CSV, including virtual no_table rows."""
        if self._loaded:
            return self._records

        records: List[ReadingRecord] = []
        observed_combos: Set[Tuple[str, int, str, str, str]] = set()

        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                site = row.get("site", "").strip()
                year = int(row.get("year", 0))
                festival = row.get("festival", "").strip()
                water_body = row.get("water_body", "").strip() or SITE_WATER_BODIES.get(site, "Bhopal Lake")
                phase = row.get("phase", "").strip()
                param = row.get("parameter", "").strip()
                raw_val = row.get("value")
                flag = row.get("flag", "").strip()
                val_printed = row.get("value_as_printed", "").strip()
                param_printed = row.get("parameter_as_printed", "").strip()
                site_printed = row.get("site_as_printed", "").strip()
                confidence = row.get("site_match_confidence", "").strip()
                source_pg = row.get("source_page", "").strip()
                unit = row.get("unit_assumed", "").strip()

                status, parsed_val = classify_reading_status(
                    value_raw=raw_val,
                    flag_raw=flag,
                    value_as_printed=val_printed,
                )

                evaluation, is_fail, is_valid, is_ambiguous = evaluate_reading_against_limits(
                    parameter=param,
                    status=status,
                    value=parsed_val,
                )

                report_file = REPORT_FILES_BY_YEAR.get(year, "")

                record = ReadingRecord(
                    year=year,
                    festival=festival,
                    site=site,
                    water_body=water_body,
                    phase=phase,
                    parameter=param,
                    value=parsed_val,
                    unit_assumed=unit,
                    flag=flag,
                    value_as_printed=val_printed,
                    parameter_as_printed=param_printed,
                    site_as_printed=site_printed,
                    site_match_confidence=confidence,
                    source_page=source_pg,
                    report_file=report_file,
                    status=status,
                    evaluation=evaluation,
                    is_fail=is_fail,
                    is_valid=is_valid,
                    is_ambiguous=is_ambiguous,
                )
                records.append(record)
                observed_combos.add((site, year, festival, phase, param))

        # Identify missing festival-year tables and emit explicit NO_TABLE records
        # For instance, Bairagarh and Malikhedi have NO Durga 2025 tables in the MPPCB report.
        for site in AUTHORITATIVE_SITES:
            water_body = SITE_WATER_BODIES.get(site, "Bhopal Lake")
            for year, fest in EXPECTED_FESTIVAL_YEARS:
                for phase in EXPECTED_PHASES:
                    for param in SCORED_PARAMETERS:
                        key = (site, year, fest, phase, param)
                        if key not in observed_combos:
                            report_file = REPORT_FILES_BY_YEAR.get(year, "")
                            unit = "mg/l" if param in ("Dissolved oxygen", "BOD") else ""
                            no_table_rec = ReadingRecord(
                                year=year,
                                festival=fest,
                                site=site,
                                water_body=water_body,
                                phase=phase,
                                parameter=param,
                                value=None,
                                unit_assumed=unit,
                                flag="no table in report",
                                value_as_printed="No table in report",
                                parameter_as_printed=param,
                                site_as_printed=site,
                                site_match_confidence="high" if site != "Rani Kamlapati ghat / Kamla Park kund" else "medium",
                                source_page="unknown",
                                report_file=report_file,
                                status=ReadingStatus.NO_TABLE,
                                evaluation=LimitEvaluation.MISSING,
                                is_fail=False,
                                is_valid=False,
                                is_ambiguous=False,
                            )
                            records.append(no_table_rec)

        self._records = records
        self._records_by_site = {}
        for r in self._records:
            self._records_by_site.setdefault(r.site, []).append(r)

        self._loaded = True
        return self._records

    def get_all_records(self) -> List[ReadingRecord]:
        """Return all loaded records."""
        if not self._loaded:
            self.load()
        return self._records

    def get_records_by_site(self, site_name: str) -> List[ReadingRecord]:
        """Return all records for a specific site."""
        if not self._loaded:
            self.load()
        return self._records_by_site.get(site_name, [])

    def get_records_by_site_id(self, site_id: str) -> List[ReadingRecord]:
        """Return all records for a specific site ID."""
        site_name = get_site_by_id(site_id)
        if not site_name:
            return []
        return self.get_records_by_site(site_name)


# Global singleton instance
loader = DataLoader()
