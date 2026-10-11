"""Brief generation module for English and Hindi decision documents."""
from datetime import date
from pathlib import Path
from typing import Dict, List
import jinja2

from app.models import BriefGhatHighlight, BriefResponse
from app.scoring import scoring_engine

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)))


def generate_brief(lang: str = "en") -> BriefResponse:
    """
    Generate a decision brief in English or Hindi.
    All figures are computed deterministically by code.
    No health claims or causal diagnosis.
    """
    ranked = scoring_engine.get_ranked_ghats()
    top_3 = ranked[:3]

    issue_date = "11 October 2026"
    event_target = "Durga Visarjan · 20 October 2026"
    target_user_role = "Bhopal Municipal Corporation (BMC) Immersion Planning Officer"

    if lang == "hi":
        title = "घाट वॉच: दुर्गा विसर्जन 2026 जल-गुणवत्ता निर्णय संक्षिप्त विवरण"
        honest_framing = (
            "यह मूल्यांकन वर्ष 2023 से 2025 के आधिकारिक म.प्र. प्रदूषण नियंत्रण बोर्ड (MPPCB) के परीक्षण डेटा पर "
            "आधारित है, वर्तमान जल गुणवत्ता पर नहीं। यह केवल सीपीसीबी क्लास-बी मानकों के सापेक्ष विचलन दर्शाता है।"
        )
        native_notice = "needs native-speaker review / मातृभाषा समीक्षा आवश्यक"

        top_highlights: List[BriefGhatHighlight] = []
        for g in top_3:
            # Hindi translations for plain reasons while keeping exact numbers and page citations
            if g.id == "bairagarh":
                reason = (
                    "घुलित ऑक्सीजन (DO) 16 में से 14 वैध परीक्षणों में 5.0 mg/l के स्नान मानक से नीचे दर्ज की गई; "
                    "न्यूनतम स्तर 0.0 mg/l (BDL) तक गिरा।"
                )
                citation = "MPPCB रिपोर्ट 2023 (गणेश विसर्जन, पृष्ठ 28)"
            elif g.id == "malikhedi":
                reason = (
                    "घुलित ऑक्सीजन (DO) 16 में से 12 वैध परीक्षणों में 5.0 mg/l के मानक से नीचे रही; "
                    "न्यूनतम स्तर 0.6 mg/l दर्ज हुआ।"
                )
                citation = "MPPCB रिपोर्ट 2024 (गणेश विसर्जन, पृष्ठ 72)"
            elif g.id == "shahpura":
                reason = (
                    "बायोकेमिकल ऑक्सीजन डिमांड (BOD) सभी 18 परीक्षणों (100%) में 3.0 mg/l के मानक से अधिक रही; "
                    "अधिकतम स्तर 11.6 mg/l दर्ज हुआ।"
                )
                citation = "MPPCB रिपोर्ट 2025 (गणेश विसर्जन, पृष्ठ 27)"
            else:
                reason = g.top_reason
                citation = "MPPCB आधिकारिक रिपोर्ट"

            top_highlights.append(
                BriefGhatHighlight(
                    rank=g.rank,
                    name=g.name,
                    water_body=g.water_body,
                    risk_score=g.risk_score,
                    risk_tier=g.risk_tier.value,
                    confidence=g.confidence.value,
                    plain_reason=reason,
                    evidence_citation=citation,
                )
            )

        recommended_checks = [
            "20 अक्टूबर 2026 से पूर्व बैरागढ़ कुंड एवं मलिकेहड़ी कुंड पर नए सिरे से जल नमूना परीक्षण को प्राथमिकता दें।",
            "विसर्जन के चरम घंटों के दौरान बैरागढ़ कुंड एवं शाहपुरा झील घाट पर अतिरिक्त जल-वातक (aeration units) तैनात करने पर विचार करें।",
            "विसर्जन के 24 घंटों के भीतर सभी घाटों से पूजा सामग्री एवं अवशेषों को निकालने हेतु सघन सफाई अभियान चलाएं।",
            "विसर्जन अवधि के दौरान त्वरित परिणाम हेतु एमपीपीसीबी क्षेत्रीय प्रयोगशाला से 24-घंटे नमूना परीक्षण का समन्वय करें।",
        ]

        data_gaps = [
            "बैरागढ़ कुंड एवं मलिकेहड़ी कुंड: आधिकारिक MPPCB 2025 रिपोर्ट में दुर्गा विसर्जन तालिका उपलब्ध नहीं है (9 निर्धारित रीडिंग अनुपलब्ध)।",
            "रानी कमलापति घाट / कमला पार्क कुंड: गणेश तालिकाओं में 'कमला पार्क कुंड' एवं दुर्गा तालिकाओं में 'लोअर लेक घाट' अंकित है (मध्यम स्थल मिलान)।",
            "टोटल कोलीफॉर्म बैक्टीरिया: सीपीसीबी क्लास-बी में अनिवार्य है परंतु एमपीपीसीबी विसर्जन रिपोर्टों में इसका परीक्षण नहीं किया गया है (परीक्षण योग्य नहीं)।",
        ]

        limitations = [
            "यह उपकरण ऐतिहासिक परीक्षण रीडिंग (2023-2025) पर आधारित है, आज की वास्तविक जल स्थिति पर नहीं।",
            "एनजीटी आदेश के पश्चात बीएमसी द्वारा निर्मित नए समर्पित विसर्जन घाट इस ऐतिहासिक डेटासेट में शामिल नहीं हैं।",
            "यह उपकरण स्वास्थ्य प्रभावों का दावा नहीं करता है और न ही प्रदूषण के कारणों का निदान करता है; यह केवल मानकों के सापेक्ष रीडिंग रिपोर्ट करता है।",
        ]

    else:
        title = "Ghat Watch: Durga Visarjan 2026 Water-Quality Decision Brief"
        honest_framing = (
            "Based on official MPPCB test readings from 2023–2025, not current water quality. "
            "Evaluates historical relative risk against CPCB Class B outdoor bathing standards."
        )
        native_notice = None

        top_highlights = []
        for g in top_3:
            if g.id == "bairagarh":
                citation = "MPPCB 2023 Report (Ganesh Visarjan, p.28)"
            elif g.id == "malikhedi":
                citation = "MPPCB 2024 Report (Ganesh Visarjan, p.72)"
            elif g.id == "shahpura":
                citation = "MPPCB 2025 Report (Ganesh Visarjan, p.27)"
            else:
                citation = "MPPCB Official Reports"

            top_highlights.append(
                BriefGhatHighlight(
                    rank=g.rank,
                    name=g.name,
                    water_body=g.water_body,
                    risk_score=g.risk_score,
                    risk_tier=g.risk_tier.value,
                    confidence=g.confidence.value,
                    plain_reason=g.top_reason,
                    evidence_citation=citation,
                )
            )

        recommended_checks = [
            "Prioritise fresh on-site water quality testing at Bairagarh kund and Malikhedi kund prior to 20 October 2026.",
            "Consider deploying mobile surface aeration units and artificial water circulation at Bairagarh kund and Shahpura lake during peak immersion hours.",
            "Schedule intensive post-immersion debris skimming and surface cleaning within 24 hours across all immersion points.",
            "Coordinate with the MPPCB regional laboratory for rapid-turnaround test sampling immediately before and after immersion.",
        ]

        data_gaps = [
            "Bairagarh kund & Malikhedi kund: No Durga visarjan monitoring table in the MPPCB 2025 report (9 scheduled readings omitted).",
            "Rani Kamlapati ghat / Kamla Park kund: Ganesh tables cite 'Kamla Park kund' while Durga tables cite 'Lower Lake ghat' (medium match confidence).",
            "Total coliform bacteria: Specified in CPCB Class B criteria but not sampled in MPPCB immersion monitoring reports (not testable).",
        ]

        limitations = [
            "Historical baseline only: Based on 2023–2025 MPPCB reports, not real-time or current water.",
            "New BMC dedicated ghats built following the NGT lake immersion directive are not covered in this historical dataset.",
            "No health claims: Does not claim medical health effects or identify specific contamination causes; reports only reading values versus statutory thresholds.",
        ]

    return BriefResponse(
        title=title,
        date=issue_date,
        target_user_role=target_user_role,
        event_target=event_target,
        honest_framing=honest_framing,
        top_ghats=top_highlights,
        recommended_checks=recommended_checks,
        data_gaps=data_gaps,
        limitations=limitations,
        language=lang,
        native_speaker_review_notice=native_notice,
    )
