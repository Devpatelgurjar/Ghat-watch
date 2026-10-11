"""Pydantic data models and schemas for Ghat Watch."""
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ReadingStatus(str, Enum):
    """Status classification for a single reading."""
    NUMERIC = "numeric"
    BELOW_DETECTION = "below_detection"
    MISSING = "missing"
    NO_TABLE = "no_table"


class LimitEvaluation(str, Enum):
    """CPCB Limit evaluation outcome."""
    PASS = "pass"
    FAIL = "fail"
    MISSING = "missing"
    NOT_SCORED = "not_scored"


class ConfidenceTier(str, Enum):
    """Coverage-based confidence tier."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RiskTier(str, Enum):
    """Risk tier based on risk score (0-100)."""
    HIGH = "High"
    ELEVATED = "Elevated"
    LOWER = "Lower relative risk"


class ReadingRecord(BaseModel):
    """Individual water quality reading record."""
    year: int
    festival: str
    site: str
    water_body: str
    phase: str
    parameter: str
    value: Optional[float] = None
    unit_assumed: str
    flag: str
    value_as_printed: str
    parameter_as_printed: str
    site_as_printed: str
    site_match_confidence: str
    source_page: str
    report_file: str
    status: ReadingStatus
    evaluation: LimitEvaluation
    is_fail: bool
    is_valid: bool
    is_ambiguous: bool = False


class ParameterStatus(BaseModel):
    """Aggregate status of a parameter for a ghat."""
    parameter: str
    cpcb_limit: str
    unit: str
    is_scored: bool
    total_readings: int
    valid_readings: int
    fail_count: int
    pass_count: int
    missing_count: int
    fail_rate_pct: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    worst_reading_display: str
    worst_source_page: Optional[str] = None
    worst_year: Optional[int] = None


class TrendPoint(BaseModel):
    """Trend data point by year and phase."""
    year: int
    festival: str
    phase: str
    do_value: Optional[float] = None
    bod_value: Optional[float] = None
    ph_value: Optional[float] = None


class GhatSummary(BaseModel):
    """Ghat ranking list item."""
    rank: int
    id: str
    name: str
    water_body: str
    risk_score: float
    risk_tier: RiskTier
    confidence: ConfidenceTier
    coverage_pct: float
    top_reason: str
    missing_share_pct: float
    caveats: List[str]


class GhatDetail(BaseModel):
    """Detailed view for an individual ghat."""
    id: str
    rank: int
    name: str
    water_body: str
    risk_score: float
    risk_tier: RiskTier
    confidence: ConfidenceTier
    coverage_pct: float
    missing_share_pct: float
    component_scores: Dict[str, float]
    parameters: List[ParameterStatus]
    evidence: List[ReadingRecord]
    trend: List[TrendPoint]
    reasons: List[str]
    caveats: List[str]


class SensitivityComparison(BaseModel):
    """Sensitivity check outcome."""
    scheme_name: str
    top_two_stable: bool
    bottom_two_stable: bool
    top_two_ghats: List[str]
    bottom_two_ghats: List[str]


class MetaResponse(BaseModel):
    """Metadata response for /api/meta."""
    tool_name: str = "Ghat Watch"
    target_event: str = "Durga Visarjan · 20 October 2026"
    target_user: str = "Bhopal Municipal Corporation (BMC) Immersion Planning Officer"
    cpcb_class: str = "Class B (Outdoor Bathing - organised)"
    limits_used: Dict[str, str]
    unscored_parameters: List[str]
    data_version: str = "MPPCB Immersion Monitoring 2023-2025 (Official Reports)"
    sensitivity_analysis: Dict[str, SensitivityComparison]
    stability_statement: str
    what_this_tool_does_not_cover: List[str]
    data_gaps: List[str]


class BriefGhatHighlight(BaseModel):
    """Top ghat highlight in the decision brief."""
    rank: int
    name: str
    water_body: str
    risk_score: float
    risk_tier: str
    confidence: str
    plain_reason: str
    evidence_citation: str


class BriefResponse(BaseModel):
    """Decision brief response in English or Hindi."""
    title: str
    date: str
    target_user_role: str
    event_target: str
    honest_framing: str
    top_ghats: List[BriefGhatHighlight]
    recommended_checks: List[str]
    data_gaps: List[str]
    limitations: List[str]
    language: str
    native_speaker_review_notice: Optional[str] = None
