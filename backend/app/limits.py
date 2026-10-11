"""CPCB Water Quality Criteria Class B (Outdoor Bathing) evaluation logic."""
from typing import Optional, Tuple
from app.config import CLASS_B_LIMITS, SCORED_PARAMETERS
from app.models import LimitEvaluation, ReadingStatus


def evaluate_reading_against_limits(
    parameter: str,
    status: ReadingStatus,
    value: Optional[float]
) -> Tuple[LimitEvaluation, bool, bool, bool]:
    """
    Evaluate a reading against CPCB Class B (outdoor bathing) standards.

    Returns:
        (evaluation, is_fail, is_valid, is_ambiguous)

    Edge Rules:
    - Missing & no_table: never valid, never pass, never fail -> LimitEvaluation.MISSING
    - Unscored parameters (COD, solids, metals, conductivity, turbidity): LimitEvaluation.NOT_SCORED
    - BDL on MINIMUM-limit parameter (Dissolved oxygen >= 5):
      Counts as FAIL (oxygen is practically depleted), flagged as AMBIGUOUS.
    - BDL on MAXIMUM-limit parameter (BOD <= 3, heavy metals):
      Counts as PASS (organic pollution / metals are below detection limit).
    """
    # 1. Non-valid readings (missing / no table)
    if status in (ReadingStatus.MISSING, ReadingStatus.NO_TABLE):
        return LimitEvaluation.MISSING, False, False, False

    # 2. Parameters not scored under CPCB Class B
    if parameter not in SCORED_PARAMETERS:
        return LimitEvaluation.NOT_SCORED, False, True, False

    # 3. Below Detection Limit (BDL / ND)
    if status == ReadingStatus.BELOW_DETECTION:
        if parameter == "Dissolved oxygen":
            # CPCB Class B minimum is 5.0 mg/l. BDL indicates virtually no dissolved oxygen.
            # Counts as FAIL and flagged ambiguous.
            return LimitEvaluation.FAIL, True, True, True
        elif parameter == "BOD":
            # CPCB Class B maximum is 3.0 mg/l. BDL indicates organic waste is below detection limit.
            # Counts as PASS.
            return LimitEvaluation.PASS, False, True, False
        elif parameter == "pH":
            # pH has a range standard (6.5 - 8.5).
            return LimitEvaluation.FAIL, True, True, True

    # 4. Numeric evaluation against CPCB Class B limits
    if status == ReadingStatus.NUMERIC and value is not None:
        if parameter == "Dissolved oxygen":
            limit = CLASS_B_LIMITS["Dissolved oxygen"]["value"]
            if value >= limit:
                return LimitEvaluation.PASS, False, True, False
            else:
                return LimitEvaluation.FAIL, True, True, False

        elif parameter == "BOD":
            limit = CLASS_B_LIMITS["BOD"]["value"]
            if value <= limit:
                return LimitEvaluation.PASS, False, True, False
            else:
                return LimitEvaluation.FAIL, True, True, False

        elif parameter == "pH":
            min_val = CLASS_B_LIMITS["pH"]["min"]
            max_val = CLASS_B_LIMITS["pH"]["max"]
            if min_val <= value <= max_val:
                return LimitEvaluation.PASS, False, True, False
            else:
                return LimitEvaluation.FAIL, True, True, False

    # Default fallback
    return LimitEvaluation.MISSING, False, False, False
