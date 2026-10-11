"""Unit tests for Checkpoint 2 (Scoring Engine & Sensitivity Analysis)."""
import pytest
from app.config import BASE_SCORING_WEIGHTS, SENSITIVITY_WEIGHT_SCHEMES
from app.models import ConfidenceTier, RiskTier
from app.scoring import ScoringEngine, get_confidence_tier, get_risk_tier


def test_ranking_contains_all_seven_ghats():
    """Verify all 7 authoritative Bhopal ghats are present and ranked 1 through 7."""
    engine = ScoringEngine()
    ranked = engine.get_ranked_ghats()
    assert len(ranked) == 7
    ranks = [g.rank for g in ranked]
    assert ranks == [1, 2, 3, 4, 5, 6, 7]

    # Verify score order is descending
    scores = [g.risk_score for g in ranked]
    assert scores == sorted(scores, reverse=True)


def test_risk_tier_naming_never_safe_or_clean():
    """Rule: Label lowest tier 'Lower relative risk', NEVER 'Safe' or 'Clean'."""
    assert get_risk_tier(80.0) == RiskTier.HIGH
    assert get_risk_tier(60.0) == RiskTier.ELEVATED
    assert get_risk_tier(35.0) == RiskTier.LOWER
    assert get_risk_tier(10.0) == RiskTier.LOWER

    for val in [0.0, 15.0, 39.0, 49.0]:
        tier = get_risk_tier(val)
        assert tier.value == "Lower relative risk"
        assert "Safe" not in tier.value
        assert "Clean" not in tier.value


def test_confidence_independent_from_risk():
    """Rule: Confidence is separate from risk, based purely on coverage, never blended."""
    assert get_confidence_tier(100.0) == ConfidenceTier.HIGH
    assert get_confidence_tier(80.0) == ConfidenceTier.HIGH
    assert get_confidence_tier(72.2) == ConfidenceTier.MEDIUM
    assert get_confidence_tier(49.0) == ConfidenceTier.LOW

    engine = ScoringEngine()
    ranked = engine.get_ranked_ghats()
    # Bairagarh has high risk (83.23) but medium confidence (72.2%)
    bairagarh = next(g for g in ranked if g.id == "bairagarh")
    assert bairagarh.risk_score > 80.0
    assert bairagarh.confidence == ConfidenceTier.MEDIUM

    # Prempura has lower relative risk (39.64) but high confidence (92.6%)
    prempura = next(g for g in ranked if g.id == "prempura")
    assert prempura.risk_score < 50.0
    assert prempura.confidence == ConfidenceTier.HIGH


def test_reasons_contain_page_references():
    """Rule: Every plain reason must link to numbers and report page numbers."""
    engine = ScoringEngine()
    ranked = engine.get_ranked_ghats()
    for g in ranked:
        assert g.top_reason is not None
        assert len(g.top_reason) > 10
        # If there were failures, reason contains page citation 'p.'
        if g.risk_score > 50:
            assert "p." in g.top_reason


def test_sensitivity_analysis_execution():
    """Verify sensitivity analysis reports stability under 3 alternative schemes."""
    engine = ScoringEngine()
    results, statement = engine.run_sensitivity_analysis()
    assert len(results) == 3
    for scheme in SENSITIVITY_WEIGHT_SCHEMES:
        assert scheme in results
        assert results[scheme].bottom_two_stable is True  # Prempura and Hathaikheda stable
    assert len(statement) > 0
