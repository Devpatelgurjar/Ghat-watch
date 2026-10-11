"""FastAPI route handlers for Ghat Watch API."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.brief import generate_brief
from app.models import BriefResponse, GhatDetail, GhatSummary, MetaResponse
from app.scoring import scoring_engine

router = APIRouter(prefix="/api", tags=["Ghat Watch"])


@router.get("/ghats", response_model=List[GhatSummary])
def get_ranked_ghats() -> List[GhatSummary]:
    """
    Get the ranked list of all 7 Bhopal immersion ghats by water quality risk.
    Ranked descending by risk score, tie-broken by lowest minimum DO, then name.
    """
    return scoring_engine.get_ranked_ghats()


@router.get("/ghats/{site_id}", response_model=GhatDetail)
def get_ghat_detail(site_id: str) -> GhatDetail:
    """
    Get detailed water quality profile, parameter evaluations vs CPCB Class B limits,
    trend timeline, and all historical evidence readings with PDF page references.
    """
    detail = scoring_engine.get_ghat_detail(site_id)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ghat with ID '{site_id}' not found. Valid IDs: bairagarh, khatlapura, prempura, rani-kamlapati, hathaikheda, malikhedi, shahpura."
        )
    return detail


@router.get("/brief", response_model=BriefResponse)
def get_decision_brief(lang: str = Query("en", pattern="^(en|hi)$")) -> BriefResponse:
    """
    Generate the one-page forwardable decision brief in English or Hindi.
    All numbers are computed by code and identical across languages.
    """
    return generate_brief(lang=lang)


@router.get("/meta", response_model=MetaResponse)
def get_metadata() -> MetaResponse:
    """
    Get system metadata, CPCB Class B statutory limits, why Class B was selected,
    what this tool does NOT cover, data gaps, and sensitivity analysis stability results.
    """
    sensitivity_results, stability_statement = scoring_engine.run_sensitivity_analysis()

    return MetaResponse(
        tool_name="Ghat Watch",
        target_event="Durga Visarjan · 20 October 2026",
        target_user="Bhopal Municipal Corporation (BMC) Immersion Planning Officer",
        cpcb_class="Class B (Outdoor Bathing - organised)",
        limits_used={
            "Dissolved oxygen": "Minimum 5.0 mg/l (tested for aquatic survival & ecological health)",
            "BOD (5 days 20°C)": "Maximum 3.0 mg/l (organic waste loading standard)",
            "pH": "Range 6.5 to 8.5 (neutral / acceptable acidity-alkalinity)",
            "Total coliform": "Maximum 500 MPN/100 ml (not tested in MPPCB reports; listed as not testable)",
        },
        unscored_parameters=[
            "COD (Chemical Oxygen Demand)",
            "Conductivity",
            "Turbidity",
            "Total solids",
            "Dissolved solids",
            "Suspended solids",
            "Chromium",
            "Lead",
            "Zinc",
            "Copper",
        ],
        data_version="MPPCB Official Immersion Monitoring Reports (2023, 2024, 2025)",
        sensitivity_analysis=sensitivity_results,
        stability_statement=stability_statement,
        what_this_tool_does_not_cover=[
            "Real-time or current water quality (evaluates historical 2023–2025 baseline only)",
            "New dedicated BMC artificial visarjan ghats built following the NGT lake immersion directive",
            "Total coliform or bacteriological safety (omitted from official immersion test tables)",
            "Medical health effects or causal attribution of pollution sources",
            "Statewide immersion sites outside Bhopal's 7 monitored ghats",
        ],
        data_gaps=[
            "Omitted 2025 Durga table: Bairagarh and Malikhedi reports lack Durga 2025 tables",
            "Name ambiguity: Rani Kamlapati ghat / Kamla Park kund site name varies across report editions",
            "No printed units: All units are inferred from standard laboratory protocols (mg/l, NTU, µS/cm)",
        ],
    )
