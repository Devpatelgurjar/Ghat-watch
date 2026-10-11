"""Unit tests for Checkpoint 1 (Backend Foundation)."""
import pytest
from app.cleaning import classify_reading_status, is_valid_reading
from app.limits import evaluate_reading_against_limits
from app.loader import DataLoader, get_site_id, get_site_by_id
from app.models import LimitEvaluation, ReadingStatus


def test_bdl_on_bod_passes():
    """Rule: BDL on a MAXIMUM-limit parameter (BOD) counts as PASS and is valid."""
    status, val = classify_reading_status(value_raw="", flag_raw="BDL", value_as_printed="BDL")
    assert status == ReadingStatus.BELOW_DETECTION
    assert val is None
    assert is_valid_reading(status) is True

    evaluation, is_fail, is_valid, is_ambiguous = evaluate_reading_against_limits(
        parameter="BOD",
        status=status,
        value=val,
    )
    assert evaluation == LimitEvaluation.PASS
    assert is_fail is False
    assert is_valid is True
    assert is_ambiguous is False


def test_bdl_on_do_fails_and_flagged_ambiguous():
    """Rule: BDL on a MINIMUM-limit parameter (Dissolved oxygen >= 5) counts as FAIL and is flagged ambiguous."""
    status, val = classify_reading_status(value_raw="", flag_raw="BDL", value_as_printed="BDL")
    assert status == ReadingStatus.BELOW_DETECTION
    assert val is None
    assert is_valid_reading(status) is True

    evaluation, is_fail, is_valid, is_ambiguous = evaluate_reading_against_limits(
        parameter="Dissolved oxygen",
        status=status,
        value=val,
    )
    assert evaluation == LimitEvaluation.FAIL
    assert is_fail is True
    assert is_valid is True
    assert is_ambiguous is True


def test_blanks_and_not_sampled_are_never_valid():
    """Rule: Blank, not sampled, _, -, *, ** are MISSING, never clean, never pass, never valid."""
    for indicator in ["", "not sampled", "_", "-", "*", "**"]:
        status, val = classify_reading_status(value_raw="", flag_raw=indicator, value_as_printed=indicator)
        assert status == ReadingStatus.MISSING
        assert val is None
        assert is_valid_reading(status) is False

        evaluation, is_fail, is_valid, is_ambiguous = evaluate_reading_against_limits(
            parameter="Dissolved oxygen",
            status=status,
            value=val,
        )
        assert evaluation == LimitEvaluation.MISSING
        assert is_fail is False
        assert is_valid is False
        assert is_ambiguous is False


def test_metals_not_scored():
    """Rule: Heavy metals (Cr, Pb, Zn, Cu) are displayed only, no limit applied, never scored."""
    for metal in ["Chromium", "Lead", "Zinc", "Copper", "COD", "Conductivity", "Turbidity"]:
        # Numeric metal reading
        status, val = classify_reading_status(value_raw="0.05", flag_raw="", value_as_printed="0.05")
        assert status == ReadingStatus.NUMERIC
        assert val == 0.05
        assert is_valid_reading(status) is True

        evaluation, is_fail, is_valid, is_ambiguous = evaluate_reading_against_limits(
            parameter=metal,
            status=status,
            value=val,
        )
        assert evaluation == LimitEvaluation.NOT_SCORED
        assert is_fail is False
        assert is_valid is True
        assert is_ambiguous is False

        # BDL metal reading
        status_bdl, val_bdl = classify_reading_status(value_raw="", flag_raw="BDL", value_as_printed="BDL")
        eval_bdl, fail_bdl, valid_bdl, _ = evaluate_reading_against_limits(
            parameter=metal,
            status=status_bdl,
            value=val_bdl,
        )
        assert eval_bdl == LimitEvaluation.NOT_SCORED
        assert fail_bdl is False
        assert valid_bdl is True


def test_no_table_for_bairagarh_and_malikhedi_durga_2025():
    """Rule: Bairagarh and Malikhedi have no Durga 2025 table in report, emitting NO_TABLE status."""
    loader = DataLoader()
    records = loader.load()

    # Bairagarh Durga 2025 records
    bairagarh_durga_2025 = [
        r for r in records
        if r.site == "Bairagarh (Sant Hirdaram) kund" and r.year == 2025 and r.festival == "Durga"
    ]
    assert len(bairagarh_durga_2025) == 9  # 3 phases * 3 scored parameters
    for r in bairagarh_durga_2025:
        assert r.status == ReadingStatus.NO_TABLE
        assert r.evaluation == LimitEvaluation.MISSING
        assert r.is_valid is False
        assert r.is_fail is False

    # Malikhedi Durga 2025 records
    malikhedi_durga_2025 = [
        r for r in records
        if r.site == "Malikhedi kund" and r.year == 2025 and r.festival == "Durga"
    ]
    assert len(malikhedi_durga_2025) == 9  # 3 phases * 3 scored parameters
    for r in malikhedi_durga_2025:
        assert r.status == ReadingStatus.NO_TABLE
        assert r.evaluation == LimitEvaluation.MISSING
        assert r.is_valid is False
        assert r.is_fail is False


def test_site_id_mappings():
    """Verify deterministic slug and canonical name mappings for all 7 ghats."""
    sites = [
        "Bairagarh (Sant Hirdaram) kund",
        "Hathaikheda dam / kund",
        "Khatlapura ghat",
        "Malikhedi kund",
        "Prempura ghat",
        "Rani Kamlapati ghat / Kamla Park kund",
        "Shahpura lake ghat",
    ]
    for site in sites:
        site_id = get_site_id(site)
        assert site_id is not None
        assert get_site_by_id(site_id) == site
