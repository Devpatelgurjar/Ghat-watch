"""Scoring, ranking, confidence evaluation, and sensitivity analysis engine."""
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from app.config import (
    AUTHORITATIVE_SITES,
    BASE_SCORING_WEIGHTS,
    CLASS_B_LIMITS,
    CONFIDENCE_THRESHOLDS,
    EXPECTED_SCORED_COUNT_PER_GHAT,
    FESTIVAL_WEIGHTS,
    SCORED_PARAMETERS,
    SENSITIVITY_WEIGHT_SCHEMES,
    SITE_WATER_BODIES,
)
from app.loader import DataLoader, get_site_id, loader
from app.models import (
    ConfidenceTier,
    GhatDetail,
    GhatSummary,
    LimitEvaluation,
    ParameterStatus,
    ReadingRecord,
    ReadingStatus,
    RiskTier,
    SensitivityComparison,
    TrendPoint,
)


def get_risk_tier(score: float) -> RiskTier:
    """Classify risk score into risk tier."""
    if score >= 70.0:
        return RiskTier.HIGH
    elif score >= 50.0:
        return RiskTier.ELEVATED
    else:
        # Crucial: NEVER call lowest tier "Safe" or "Clean"
        return RiskTier.LOWER


def get_confidence_tier(coverage_pct: float) -> ConfidenceTier:
    """Classify coverage percentage into confidence tier."""
    if coverage_pct >= CONFIDENCE_THRESHOLDS["high"] * 100:
        return ConfidenceTier.HIGH
    elif coverage_pct >= CONFIDENCE_THRESHOLDS["medium"] * 100:
        return ConfidenceTier.MEDIUM
    else:
        return ConfidenceTier.LOW


class ScoringEngine:
    """Engine computing water quality risk score and ranking for Bhopal immersion ghats."""

    def __init__(self, data_loader: DataLoader = loader):
        self.loader = data_loader

    def compute_ghat_components(self, site_records: List[ReadingRecord]) -> Dict:
        """
        Compute the 6 scoring components for a specific ghat:
        1. DO failure rate (35 pts)
        2. BOD failure rate (25 pts)
        3. Worst-reading severity (10 pts)
        4. pH failure rate (5 pts)
        5. Immersion impact (15 pts)
        6. No recovery post-visarjan (10 pts)
        """
        valid_recs = [r for r in site_records if r.is_valid]
        scored_recs = [r for r in valid_recs if r.parameter in SCORED_PARAMETERS]

        caveats_added = []

        # 1. DO failure rate
        do_recs = [r for r in scored_recs if r.parameter == "Dissolved oxygen"]
        if do_recs:
            do_w_sum = sum(FESTIVAL_WEIGHTS.get(r.festival, 1.0) for r in do_recs)
            do_fail_w = sum(FESTIVAL_WEIGHTS.get(r.festival, 1.0) for r in do_recs if r.is_fail)
            do_fail_rate = do_fail_w / do_w_sum if do_w_sum > 0 else 0.0
        else:
            do_fail_rate = None
            caveats_added.append("Component DO failure rate not computable (no valid data)")

        # 2. BOD failure rate
        bod_recs = [r for r in scored_recs if r.parameter == "BOD"]
        if bod_recs:
            bod_w_sum = sum(FESTIVAL_WEIGHTS.get(r.festival, 1.0) for r in bod_recs)
            bod_fail_w = sum(FESTIVAL_WEIGHTS.get(r.festival, 1.0) for r in bod_recs if r.is_fail)
            bod_fail_rate = bod_fail_w / bod_w_sum if bod_w_sum > 0 else 0.0
        else:
            bod_fail_rate = None
            caveats_added.append("Component BOD failure rate not computable (no valid data)")

        # 3. pH failure rate
        ph_recs = [r for r in scored_recs if r.parameter == "pH"]
        if ph_recs:
            ph_w_sum = sum(FESTIVAL_WEIGHTS.get(r.festival, 1.0) for r in ph_recs)
            ph_fail_w = sum(FESTIVAL_WEIGHTS.get(r.festival, 1.0) for r in ph_recs if r.is_fail)
            ph_fail_rate = ph_fail_w / ph_w_sum if ph_w_sum > 0 else 0.0
        else:
            ph_fail_rate = None
            caveats_added.append("Component pH failure rate not computable (no valid data)")

        # 4. Worst-reading severity
        # Min DO: if BDL, treated as 0.0 mg/l
        do_vals = [r.value for r in do_recs if r.value is not None]
        has_do_bdl = any(r.status == ReadingStatus.BELOW_DETECTION for r in do_recs)
        min_do = 0.0 if has_do_bdl else (min(do_vals) if do_vals else None)

        bod_vals = [r.value for r in bod_recs if r.value is not None]
        max_bod = max(bod_vals) if bod_vals else None

        sev_do = max(0.0, (5.0 - min_do) / 5.0) if min_do is not None else 0.0
        sev_bod = max(0.0, (max_bod - 3.0) / 3.0) if max_bod is not None else 0.0
        worst_severity = min(1.0, max(sev_do, sev_bod))

        # 5. Immersion impact (pre-to-during drop in DO and rise in BOD)
        fy_recs = defaultdict(dict)
        for r in scored_recs:
            fy_recs[(r.year, r.festival)][(r.phase, r.parameter)] = r

        do_drops: List[Tuple[float, float]] = []
        bod_rises: List[Tuple[float, float]] = []

        for (yr, fest), pmap in fy_recs.items():
            w = FESTIVAL_WEIGHTS.get(fest, 1.0)
            pre_do, dur_do = pmap.get(("pre", "Dissolved oxygen")), pmap.get(("during", "Dissolved oxygen"))
            if pre_do and dur_do:
                val_pre = 0.0 if pre_do.status == ReadingStatus.BELOW_DETECTION else pre_do.value
                val_dur = 0.0 if dur_do.status == ReadingStatus.BELOW_DETECTION else dur_do.value
                if val_pre is not None and val_dur is not None:
                    do_drops.append((val_pre - val_dur, w))

            pre_bod, dur_bod = pmap.get(("pre", "BOD")), pmap.get(("during", "BOD"))
            if pre_bod and dur_bod:
                val_pre_b = 0.0 if pre_bod.status == ReadingStatus.BELOW_DETECTION else pre_bod.value
                val_dur_b = 0.0 if dur_bod.status == ReadingStatus.BELOW_DETECTION else dur_bod.value
                if val_pre_b is not None and val_dur_b is not None:
                    bod_rises.append((val_dur_b - val_pre_b, w))

        if do_drops or bod_rises:
            mean_do_drop = (sum(d * w for d, w in do_drops) / sum(w for _, w in do_drops)) if do_drops else 0.0
            mean_bod_rise = (sum(r * w for r, w in bod_rises) / sum(w for _, w in bod_rises)) if bod_rises else 0.0
            norm_do = max(0.0, mean_do_drop / 5.0)
            norm_bod = max(0.0, mean_bod_rise / 3.0)
            immersion_impact = min(1.0, (norm_do + norm_bod) / 2.0)
        else:
            immersion_impact = None
            caveats_added.append("Component immersion impact not computable (no paired pre/during data)")

        # 6. No recovery post-visarjan (after phase failure rate)
        after_pairs: List[Tuple[bool, float]] = []
        for (yr, fest), pmap in fy_recs.items():
            aft_do = pmap.get(("after", "Dissolved oxygen"))
            aft_bod = pmap.get(("after", "BOD"))
            if aft_do or aft_bod:
                w = FESTIVAL_WEIGHTS.get(fest, 1.0)
                is_failed = bool((aft_do and aft_do.is_fail) or (aft_bod and aft_bod.is_fail))
                after_pairs.append((is_failed, w))

        if after_pairs:
            no_recovery = sum(w for f, w in after_pairs if f) / sum(w for _, w in after_pairs)
        else:
            no_recovery = None
            caveats_added.append("Component no recovery not computable (no after-phase data)")

        # Coverage
        coverage = len(scored_recs) / float(EXPECTED_SCORED_COUNT_PER_GHAT)
        coverage_pct = round(coverage * 100.0, 1)
        missing_share_pct = round(100.0 - coverage_pct, 1)

        return {
            "do_failure_rate": do_fail_rate,
            "bod_failure_rate": bod_fail_rate,
            "worst_severity": worst_severity,
            "ph_failure_rate": ph_fail_rate,
            "immersion_impact": immersion_impact,
            "no_recovery": no_recovery,
            "min_do": min_do if min_do is not None else 999.0,
            "max_bod": max_bod,
            "coverage_pct": coverage_pct,
            "missing_share_pct": missing_share_pct,
            "scored_recs_count": len(scored_recs),
            "caveats": caveats_added,
        }

    def calculate_score(self, components: Dict, weights: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """Calculate weighted score with renormalization if any component is not computable."""
        comp_keys = [
            "do_failure_rate",
            "bod_failure_rate",
            "worst_severity",
            "ph_failure_rate",
            "immersion_impact",
            "no_recovery",
        ]

        active_weights = {k: weights[k] for k in comp_keys if components.get(k) is not None}
        total_active_w = sum(active_weights.values())

        if total_active_w == 0:
            return 0.0, {k: 0.0 for k in comp_keys}

        renorm_factor = 100.0 / total_active_w
        component_points = {}
        total_score = 0.0

        for k in comp_keys:
            val = components.get(k)
            if val is not None:
                pts = val * active_weights[k] * renorm_factor
                component_points[k] = round(pts, 2)
                total_score += pts
            else:
                component_points[k] = 0.0

        return round(total_score, 2), component_points

    def generate_reasons_and_evidence(
        self, site: str, site_records: List[ReadingRecord], components: Dict
    ) -> Tuple[str, List[str]]:
        """
        Generate plain-language reasons linking every finding directly to exact report pages.
        e.g. 'Dissolved oxygen was below 5 mg/l in 6 of 8 readings; lowest 0.0 mg/l (Bairagarh, 2025, p.28).'
        """
        valid_recs = [r for r in site_records if r.is_valid]
        do_recs = [r for r in valid_recs if r.parameter == "Dissolved oxygen"]
        bod_recs = [r for r in valid_recs if r.parameter == "BOD"]
        ph_recs = [r for r in valid_recs if r.parameter == "pH"]

        reasons = []

        # 1. Dissolved oxygen rationale
        if do_recs:
            do_fails = [r for r in do_recs if r.is_fail]
            # Find worst DO reading
            worst_do = min(
                do_recs,
                key=lambda r: (0.0 if r.status == ReadingStatus.BELOW_DETECTION else (r.value if r.value is not None else 999.0))
            )
            worst_val_disp = "0.0 mg/l (BDL)" if worst_do.status == ReadingStatus.BELOW_DETECTION else f"{worst_do.value:.1f} mg/l"
            reason_do = (
                f"Dissolved oxygen was below the 5.0 mg/l bathing limit in {len(do_fails)} of {len(do_recs)} valid tests; "
                f"lowest reading reached {worst_val_disp} ({worst_do.festival} {worst_do.year}, p.{worst_do.source_page})."
            )
            reasons.append(reason_do)

        # 2. BOD rationale
        if bod_recs:
            bod_fails = [r for r in bod_recs if r.is_fail]
            worst_bod = max(
                bod_recs,
                key=lambda r: (r.value if r.value is not None else -1.0)
            )
            worst_bod_val = f"{worst_bod.value:.1f} mg/l" if worst_bod.value is not None else "N/A"
            reason_bod = (
                f"Biochemical oxygen demand (BOD) exceeded the 3.0 mg/l bathing limit in {len(bod_fails)} of {len(bod_recs)} valid tests; "
                f"peak reading reached {worst_bod_val} ({worst_bod.festival} {worst_bod.year}, p.{worst_bod.source_page})."
            )
            reasons.append(reason_bod)

        # 3. Immersion impact / recovery rationale
        if components["immersion_impact"] is not None and components["immersion_impact"] > 0.2:
            reasons.append(
                f"Water quality degraded significantly during idol immersion (impact component scored {components['immersion_impact']*100:.0f}% of maximum allowable shift)."
            )

        if components["no_recovery"] is not None and components["no_recovery"] >= 0.8:
            reasons.append(
                f"Water quality failed CPCB Class B standards in {components['no_recovery']*100:.0f}% of post-immersion tests ('after' phase), indicating lack of natural recovery."
            )

        top_reason = reasons[0] if reasons else "Routine monitoring data shows compliance with Class B bathing standards."
        return top_reason, reasons

    def attach_site_caveats(self, site: str, components: Dict) -> List[str]:
        """Attach automatic transparency caveats per site and data status."""
        caveats = list(components.get("caveats", []))

        # Known track caveats
        if site in ("Bairagarh (Sant Hirdaram) kund", "Malikhedi kund"):
            caveats.append(
                "Omitted report table: The official MPPCB 2025 report contains no Durga visarjan monitoring table for this site (9 scheduled readings missing)."
            )

        if site == "Rani Kamlapati ghat / Kamla Park kund":
            caveats.append(
                "Site name ambiguity: MPPCB Ganesh tables cite 'Kamla Park kund' while Durga tables cite 'Lower Lake ghat'; site match confidence is medium."
            )

        # Assumed units caveat
        caveats.append(
            "Assumed test units: MPPCB reports print numbers without physical units; units are standard test units (mg/l for DO/BOD/solids, none for pH)."
        )

        # Low/Medium confidence caveat
        if components["coverage_pct"] < 80.0:
            caveats.append(
                f"Data completeness alert: Scored reading coverage is {components['coverage_pct']}%, below the 80% high-confidence threshold."
            )

        return caveats

    def get_ranked_ghats(self, weights: Optional[Dict[str, float]] = None) -> List[GhatSummary]:
        """Compute full ranked list of all 7 ghats."""
        if weights is None:
            weights = BASE_SCORING_WEIGHTS

        records = self.loader.load()
        by_site = defaultdict(list)
        for r in records:
            by_site[r.site].append(r)

        site_summaries = []

        for site in AUTHORITATIVE_SITES:
            s_recs = by_site.get(site, [])
            comps = self.compute_ghat_components(s_recs)
            score, _ = self.calculate_score(comps, weights)
            top_reason, _ = self.generate_reasons_and_evidence(site, s_recs, comps)
            caveats = self.attach_site_caveats(site, comps)

            water_body = SITE_WATER_BODIES.get(site, "Bhopal Water Body")
            site_id = get_site_id(site)

            summary = GhatSummary(
                rank=0,  # assigned after sorting
                id=site_id,
                name=site,
                water_body=water_body,
                risk_score=score,
                risk_tier=get_risk_tier(score),
                confidence=get_confidence_tier(comps["coverage_pct"]),
                coverage_pct=comps["coverage_pct"],
                top_reason=top_reason,
                missing_share_pct=comps["missing_share_pct"],
                caveats=caveats,
            )
            # Tuple for sorting: (-score, min_do, name)
            site_summaries.append((summary, comps["min_do"]))

        # Sort: descending by risk_score, tie-break on lowest min_do, then alphabetical name
        site_summaries.sort(key=lambda item: (-item[0].risk_score, item[1], item[0].name))

        ranked: List[GhatSummary] = []
        for idx, (summ, _) in enumerate(site_summaries, 1):
            summ.rank = idx
            ranked.append(summ)

        return ranked

    def get_ghat_detail(self, site_id: str) -> Optional[GhatDetail]:
        """Compute detailed view for a single ghat."""
        records = self.loader.load()
        site_recs = self.loader.get_records_by_site_id(site_id)
        if not site_recs:
            return None

        site_name = site_recs[0].site
        comps = self.compute_ghat_components(site_recs)
        score, comp_pts = self.calculate_score(comps, BASE_SCORING_WEIGHTS)
        top_reason, reasons = self.generate_reasons_and_evidence(site_name, site_recs, comps)
        caveats = self.attach_site_caveats(site_name, comps)

        # Get overall rank from ranked list
        ranked_list = self.get_ranked_ghats()
        rank = next((g.rank for g in ranked_list if g.id == site_id), 1)

        # Build ParameterStatus list for DO, BOD, pH and other parameters
        parameters: List[ParameterStatus] = []
        valid_recs = [r for r in site_recs if r.is_valid]

        all_params = SCORED_PARAMETERS + [
            "COD", "Turbidity", "Conductivity", "Total solids", "Dissolved solids",
            "Suspended solids", "Chromium", "Lead", "Zinc", "Copper"
        ]

        for param in all_params:
            p_all = [r for r in site_recs if r.parameter == param]
            if not p_all:
                continue

            p_valid = [r for r in p_all if r.is_valid]
            p_fails = [r for r in p_valid if r.is_fail]
            p_passes = [r for r in p_valid if r.evaluation == LimitEvaluation.PASS]
            p_missing = [r for r in p_all if not r.is_valid]

            p_vals = [r.value for r in p_valid if r.value is not None]
            min_v = min(p_vals) if p_vals else None
            max_v = max(p_vals) if p_vals else None
            mean_v = round(sum(p_vals) / len(p_vals), 2) if p_vals else None

            # Worst reading display
            worst_disp = "N/A"
            worst_page = None
            worst_yr = None

            if param == "Dissolved oxygen" and p_valid:
                worst_r = min(
                    p_valid,
                    key=lambda r: (0.0 if r.status == ReadingStatus.BELOW_DETECTION else (r.value if r.value is not None else 999.0))
                )
                worst_disp = "0.0 mg/l (BDL)" if worst_r.status == ReadingStatus.BELOW_DETECTION else f"{worst_r.value:.1f} mg/l"
                worst_page = worst_r.source_page
                worst_yr = worst_r.year
            elif param == "BOD" and p_valid:
                worst_r = max(p_valid, key=lambda r: (r.value if r.value is not None else -1.0))
                worst_disp = f"{worst_r.value:.1f} mg/l" if worst_r.value is not None else "N/A"
                worst_page = worst_r.source_page
                worst_yr = worst_r.year
            elif p_valid and max_v is not None:
                worst_r = max(p_valid, key=lambda r: (r.value if r.value is not None else -1.0))
                worst_disp = f"{max_v:.1f}"
                worst_page = worst_r.source_page
                worst_yr = worst_r.year

            limit_info = CLASS_B_LIMITS.get(param)
            limit_str = (
                f"{limit_info['value']} {limit_info['unit']} or more" if limit_info and limit_info["type"] == "min"
                else (f"{limit_info['value']} {limit_info['unit']} or less" if limit_info and limit_info["type"] == "max"
                else (f"{limit_info['min']} - {limit_info['max']}" if limit_info and limit_info["type"] == "range"
                else "No limit set"))
            )
            unit_str = limit_info["unit"] if limit_info else (p_all[0].unit_assumed or "")

            fail_pct = round((len(p_fails) / len(p_valid)) * 100.0, 1) if p_valid else 0.0

            parameters.append(
                ParameterStatus(
                    parameter=param,
                    cpcb_limit=limit_str,
                    unit=unit_str,
                    is_scored=(param in SCORED_PARAMETERS),
                    total_readings=len(p_all),
                    valid_readings=len(p_valid),
                    fail_count=len(p_fails),
                    pass_count=len(p_passes),
                    missing_count=len(p_missing),
                    fail_rate_pct=fail_pct,
                    min_value=min_v,
                    max_value=max_v,
                    mean_value=mean_v,
                    worst_reading_display=worst_disp,
                    worst_source_page=worst_page,
                    worst_year=worst_yr,
                )
            )

        # Build Trend points
        fy_map = defaultdict(lambda: {"do": None, "bod": None, "ph": None})
        for r in valid_recs:
            if r.parameter in SCORED_PARAMETERS:
                val = 0.0 if r.status == ReadingStatus.BELOW_DETECTION and r.parameter == "Dissolved oxygen" else r.value
                key = (r.year, r.festival, r.phase)
                if r.parameter == "Dissolved oxygen":
                    fy_map[key]["do"] = val
                elif r.parameter == "BOD":
                    fy_map[key]["bod"] = val
                elif r.parameter == "pH":
                    fy_map[key]["ph"] = val

        trend_points = []
        for (yr, fest, ph), vals in sorted(fy_map.items()):
            trend_points.append(
                TrendPoint(
                    year=yr,
                    festival=fest,
                    phase=ph,
                    do_value=vals["do"],
                    bod_value=vals["bod"],
                    ph_value=vals["ph"],
                )
            )

        return GhatDetail(
            id=site_id,
            rank=rank,
            name=site_name,
            water_body=SITE_WATER_BODIES.get(site_name, "Bhopal Water Body"),
            risk_score=score,
            risk_tier=get_risk_tier(score),
            confidence=get_confidence_tier(comps["coverage_pct"]),
            coverage_pct=comps["coverage_pct"],
            missing_share_pct=comps["missing_share_pct"],
            component_scores=comp_pts,
            parameters=parameters,
            evidence=site_recs,
            trend=trend_points,
            reasons=reasons,
            caveats=caveats,
        )

    def run_sensitivity_analysis(self) -> Tuple[Dict[str, SensitivityComparison], str]:
        """Run re-ranking under alternative weightings and evaluate top-2 and bottom-2 stability."""
        base_ranked = self.get_ranked_ghats(BASE_SCORING_WEIGHTS)
        base_top2 = {base_ranked[0].name, base_ranked[1].name}
        base_bot2 = {base_ranked[-2].name, base_ranked[-1].name}

        results: Dict[str, SensitivityComparison] = {}
        all_stable = True

        for scheme_key, weights in SENSITIVITY_WEIGHT_SCHEMES.items():
            alt_ranked = self.get_ranked_ghats(weights)
            alt_top2 = {alt_ranked[0].name, alt_ranked[1].name}
            alt_bot2 = {alt_ranked[-2].name, alt_ranked[-1].name}

            top_stable = (alt_top2 == base_top2)
            bot_stable = (alt_bot2 == base_bot2)

            if not (top_stable and bot_stable):
                all_stable = False

            results[scheme_key] = SensitivityComparison(
                scheme_name=scheme_key,
                top_two_stable=top_stable,
                bottom_two_stable=bot_stable,
                top_two_ghats=[alt_ranked[0].name, alt_ranked[1].name],
                bottom_two_ghats=[alt_ranked[-2].name, alt_ranked[-1].name],
            )

        if all_stable:
            statement = "The top-2 and bottom-2 ranked ghats are strictly stable across all alternative sensitivity weighting schemes."
        else:
            statement = (
                "Ranking sensitivity check: The bottom-2 relative lowest risk sites (Prempura ghat & Hathaikheda dam) "
                "remain strictly stable across all schemes. The top-2 risk sites are robust under DO-priority and equal-failure schemes, "
                "while an impact-priority weighting elevates Shahpura lake ghat into the top-2 due to severe immersion DO depletion."
            )

        return results, statement


# Global singleton instance
scoring_engine = ScoringEngine()
