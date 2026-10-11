# Ghat Watch (घाट वॉच)

**Decision-Support Water Quality System for Bhopal Durga Visarjan (20 October 2026)**  
*Claude Impact Lab × Cerebras Café Compute Hackathon, Bhopal*  
**Track 2: Visarjan Ghat Watch**  
*Code offered to the Government of Madhya Pradesh (MPSeDC & Bhopal Municipal Corporation)*

---

## 1. The One User & Purpose

**Target User:** A single Bhopal Municipal Corporation (BMC) field officer responsible for planning idol immersion logistics, mobile aeration units, fresh testing, and post-visarjan cleaning ahead of **Durga Visarjan on 20 October 2026**.

**The Problem:** The MP Pollution Control Board (MPPCB) monitors water quality before, during, and one week after immersion cycles, publishing results across dense 90–120 page annual PDFs. Historically, this data sat unread, and immersion planning relied on memory.

**The Solution:** Ghat Watch ingests all 1,524 test readings from 2023–2025 across Bhopal's 7 official immersion sites, evaluates them against **CPCB Class B (Outdoor Bathing)** standards, ranks the ghats by historical water-quality vulnerability, explains every rank in plain words, links every number directly to its original report page, and generates a printable one-page bilingual brief (English and हिन्दी).

---

## 2. How to Run (3 Steps)

### Option A: Docker Compose (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/your-org/ghat-watch.git
cd ghat-watch

# 2. Start all services
docker compose up --build

# 3. Open in browser
# Frontend: http://localhost:3000
# Backend API & Docs: http://localhost:8000/docs
```

### Option B: Local Development
```bash
# 1. Start Backend (Terminal 1)
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
$env:PYTHONPATH="."
.venv/Scripts/uvicorn app.main:app --port 8000 --reload

# 2. Start Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# 3. Open http://localhost:3000
```

---

## 3. What Works & What Doesn't

### What Works
- **7 Ghat Vulnerability Ranking:** Deterministic 0–100 risk score based on Dissolved Oxygen failure ($35\%$), BOD failure ($25\%$), worst reading severity ($10\%$), pH failure ($5\%$), immersion drop ($15\%$), and lack of post-visarjan recovery ($10\%$) with festival weighting ($1.5\times$ Durga, $1.0\times$ Ganesh).
- **Separation of Confidence:** Data completeness coverage ($<50\%$ Low, $50\text{--}79\%$ Medium, $\ge 80\%$ High) is strictly independent of risk score.
- **Traceable Evidence Trail:** Every number links directly to its source PDF report page via `/reports/<filename>.pdf#page=N`.
- **Hatched Missing Data:** Blank or unrecorded entries are visually styled with diagonal hatching and labeled "Missing" or "No Table" (never green, never blank, never treated as clean).
- **Asymmetric BDL Handling:** Below Detection Limit (BDL) on BOD passes; BDL on Dissolved Oxygen fails and is flagged `ambiguous`.
- **Forwardable Bilingual Brief:** Formatted for single-sheet A4 printing in English and Hindi (with standard Devanagari typography and visible native-speaker review notice).
- **Sensitivity Analysis:** Live `/api/meta` endpoint reporting stability of top-2 and bottom-2 ranked ghats under 3 alternative weighting models.

### What Doesn't / Intentional Exclusions
- **No User Accounts:** Single-user workflow with no authentication, database, or admin portals.
- **No Scraping:** Operates solely on verified public data in `data/` and `resources/`.
- **No LLM Numbers:** All brief metrics and rank rationales are computed in code.
- **Phase 2 Map:** Reserved strictly as a post-approval extension with unverified coordinate fences.

---

## 4. What This Tool Does NOT Cover (Operational Scope)

1. **Current Water Quality:** This tool evaluates historical 2023–2025 MPPCB test baselines. It does **not** measure real-time water conditions on 20 October 2026.
2. **New Dedicated BMC Ghats:** Does not cover artificial immersion ponds constructed recently following the NGT lake immersion directive.
3. **Coliform Bacteria:** CPCB Class B mandates total coliform $\le 500\text{ MPN/100ml}$, but this was omitted from official immersion reports; listed as *not testable*.
4. **Zero Health Claims:** This tool never claims medical symptoms, sickness, or pollution causes. It only states *"reading X vs limit Y"*.
5. **Statewide Sites:** Focuses exclusively on Bhopal's 7 monitored immersion ghats.

---

## 5. Authoritative Data Sources

| Document | Source Link | Notes |
|---|---|---|
| **MPPCB Ganesh & Durga Visarjan Report 2025** | [mppcb.mp.gov.in (2025)](https://www.mppcb.mp.gov.in/proc/mon/Ganesh_and_Durga_visarjan_report-2025.pdf) | 92 pages; local PDF served at `/reports/` |
| **MPPCB Ganesh & Durga Visarjan Report 2024** | [mppcb.mp.gov.in (2024)](https://www.mppcb.mp.gov.in/proc/mon/Ganesh_and_Durga_visarjan_report-2024.pdf) | 118 pages; local PDF served at `/reports/` |
| **MPPCB Idol Immersion Report 2023 (CPCB format)** | [mppcb.mp.gov.in (2023)](https://www.mppcb.mp.gov.in/proc/mon/Idol_immer._Report_23_CPCB.pdf) | 87 pages; local PDF served at `/reports/` |
| **CPCB Water Quality Criteria (Classes A–E)** | [cpcb.gov.in](https://cpcb.gov.in/water-quality-criteria/) | Official statutory criteria for Class B outdoor bathing |

---

## 6. Hand-Check Reproducibility (2 Example Ghats)

### Example 1: Bairagarh (Sant Hirdaram) kund
- **DO Failures:** 11 of 13 valid readings below $5.0\text{ mg/l}$; weighted fail rate $= 87.5\%$ ($30.62\text{ pts}$).
- **BOD Failures:** 13 of 13 valid readings exceed $3.0\text{ mg/l}$; weighted fail rate $= 100\%$ ($25.00\text{ pts}$).
- **Worst Severity:** Min DO is $0.0\text{ mg/l}$ (BDL), severity $= 1.0$ ($10.00\text{ pts}$).
- **pH Failures:** 0 failures ($0.00\text{ pts}$).
- **Immersion Impact:** $7.61\text{ pts}$.
- **No Recovery:** Post-visarjan water failed Class B in $100\%$ of "after" tests ($10.00\text{ pts}$).
- **Total Score:** $83.23 / 100$ $\to$ **Rank #1 (High Risk)**. Scored coverage: $72.2\%$ (Medium confidence due to omitted Durga 2025 table).

### Example 2: Prempura ghat
- **DO Failures:** 3 of 18 readings below $5.0\text{ mg/l}$; weighted fail rate $= 15.6\%$ ($5.44\text{ pts}$).
- **BOD Failures:** 11 of 17 readings exceed $3.0\text{ mg/l}$; weighted fail rate $= 61.1\%$ ($15.28\text{ pts}$).
- **Worst Severity:** Max BOD is $6.8\text{ mg/l}$, severity $= 1.0$ ($10.00\text{ pts}$).
- **pH Failures:** $9.5\%$ weighted fail rate ($0.48\text{ pts}$).
- **Immersion Impact:** $3.11\text{ pts}$.
- **No Recovery:** $53.3\%$ failure in "after" tests ($5.33\text{ pts}$).
- **Total Score:** $39.64 / 100$ $\to$ **Rank #7 (Lower relative risk)**. Scored coverage: $92.6\%$ (High confidence).

---

## 7. Automated Test Suite

Run full backend unit and integration tests:
```powershell
backend\.venv\Scripts\python.exe -m pytest -v
```
All 16 tests covering limits evaluation, asymmetric BDL handling, missing flag mapping, scoring components, sensitivity analysis, and API contracts pass in $<1$ second.

---

## 8. License
Released under the [MIT License](LICENSE).
Offered to the Government of Madhya Pradesh (MPSeDC and Bhopal Municipal Corporation).
