/**
 * TypeScript definitions matching the Ghat Watch backend API schemas.
 */

export type ReadingStatus = 'numeric' | 'below_detection' | 'missing' | 'no_table';
export type LimitEvaluation = 'pass' | 'fail' | 'missing' | 'not_scored';
export type ConfidenceTier = 'High' | 'Medium' | 'Low';
export type RiskTier = 'High' | 'Elevated' | 'Lower relative risk';

export interface ReadingRecord {
  year: number;
  festival: string;
  site: string;
  water_body: string;
  phase: string;
  parameter: string;
  value: number | null;
  unit_assumed: string;
  flag: string;
  value_as_printed: string;
  parameter_as_printed: string;
  site_as_printed: string;
  site_match_confidence: string;
  source_page: string;
  report_file: string;
  status: ReadingStatus;
  evaluation: LimitEvaluation;
  is_fail: boolean;
  is_valid: boolean;
  is_ambiguous: boolean;
}

export interface ParameterStatus {
  parameter: string;
  cpcb_limit: string;
  unit: string;
  is_scored: boolean;
  total_readings: number;
  valid_readings: number;
  fail_count: number;
  pass_count: number;
  missing_count: number;
  fail_rate_pct: number;
  min_value: number | null;
  max_value: number | null;
  mean_value: number | null;
  worst_reading_display: string;
  worst_source_page: string | null;
  worst_year: number | null;
}

export interface TrendPoint {
  year: number;
  festival: string;
  phase: string;
  do_value: number | null;
  bod_value: number | null;
  ph_value: number | null;
}

export interface GhatSummary {
  rank: number;
  id: string;
  name: string;
  water_body: string;
  risk_score: number;
  risk_tier: RiskTier;
  confidence: ConfidenceTier;
  coverage_pct: number;
  top_reason: string;
  missing_share_pct: number;
  caveats: string[];
}

export interface GhatDetail {
  id: string;
  rank: number;
  name: string;
  water_body: string;
  risk_score: number;
  risk_tier: RiskTier;
  confidence: ConfidenceTier;
  coverage_pct: number;
  missing_share_pct: number;
  component_scores: Record<string, number>;
  parameters: ParameterStatus[];
  evidence: ReadingRecord[];
  trend: TrendPoint[];
  reasons: string[];
  caveats: string[];
}

export interface SensitivityComparison {
  scheme_name: string;
  top_two_stable: boolean;
  bottom_two_stable: boolean;
  top_two_ghats: string[];
  bottom_two_ghats: string[];
}

export interface MetaResponse {
  tool_name: string;
  target_event: string;
  target_user: string;
  cpcb_class: string;
  limits_used: Record<string, string>;
  unscored_parameters: string[];
  data_version: string;
  sensitivity_analysis: Record<string, SensitivityComparison>;
  stability_statement: string;
  what_this_tool_does_not_cover: string[];
  data_gaps: string[];
}

export interface BriefGhatHighlight {
  rank: number;
  name: string;
  water_body: string;
  risk_score: number;
  risk_tier: string;
  confidence: string;
  plain_reason: string;
  evidence_citation: string;
}

export interface BriefResponse {
  title: string;
  date: string;
  target_user_role: string;
  event_target: string;
  honest_framing: string;
  top_ghats: BriefGhatHighlight[];
  recommended_checks: string[];
  data_gaps: string[];
  limitations: string[];
  language: string;
  native_speaker_review_notice?: string | null;
}
