"""Integration tests for FastAPI endpoints (Checkpoint 3)."""
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_api_ghats_ranked_list():
    """Verify GET /api/ghats returns 7 ranked ghats with correct fields."""
    response = client.get("/api/ghats")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7

    # Check order
    scores = [g["risk_score"] for g in data]
    assert scores == sorted(scores, reverse=True)

    # Check rank numbers 1..7
    ranks = [g["rank"] for g in data]
    assert ranks == [1, 2, 3, 4, 5, 6, 7]

    # Verify fields in each item
    for g in data:
        assert "rank" in g
        assert "id" in g
        assert "name" in g
        assert "water_body" in g
        assert "risk_score" in g
        assert "confidence" in g
        assert "top_reason" in g
        assert "missing_share_pct" in g
        assert "caveats" in g
        assert isinstance(g["caveats"], list)


def test_api_ghat_detail():
    """Verify GET /api/ghats/{id} returns full detail profile with parameters, trend, and evidence."""
    response = client.get("/api/ghats/bairagarh")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "bairagarh"
    assert data["name"] == "Bairagarh (Sant Hirdaram) kund"
    assert "parameters" in data
    assert len(data["parameters"]) > 0
    assert "evidence" in data
    assert len(data["evidence"]) > 0
    assert "trend" in data
    assert len(data["trend"]) > 0
    assert "reasons" in data
    assert len(data["reasons"]) > 0
    assert "caveats" in data
    assert len(data["caveats"]) > 0

    # Verify evidence items have source_page and report_file
    for ev in data["evidence"]:
        assert "source_page" in ev
        assert "report_file" in ev
        assert "status" in ev
        assert "evaluation" in ev


def test_api_ghat_detail_unknown_404():
    """Verify GET /api/ghats/{id} returns 404 for unknown id."""
    response = client.get("/api/ghats/nonexistent-ghat")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_api_brief_en_and_hi():
    """Verify GET /api/brief returns brief in English and Hindi with identical numeric values."""
    res_en = client.get("/api/brief?lang=en")
    assert res_en.status_code == 200
    brief_en = res_en.json()

    assert brief_en["language"] == "en"
    assert len(brief_en["top_ghats"]) == 3
    assert len(brief_en["recommended_checks"]) > 0
    assert len(brief_en["data_gaps"]) > 0
    assert len(brief_en["limitations"]) > 0
    assert brief_en["native_speaker_review_notice"] is None

    res_hi = client.get("/api/brief?lang=hi")
    assert res_hi.status_code == 200
    brief_hi = res_hi.json()

    assert brief_hi["language"] == "hi"
    assert len(brief_hi["top_ghats"]) == 3
    assert brief_hi["native_speaker_review_notice"] is not None
    assert "needs native-speaker review" in brief_hi["native_speaker_review_notice"]

    # Verify numbers match across both languages
    for idx in range(3):
        en_g = brief_en["top_ghats"][idx]
        hi_g = brief_hi["top_ghats"][idx]
        assert en_g["rank"] == hi_g["rank"]
        assert en_g["risk_score"] == hi_g["risk_score"]


def test_api_meta():
    """Verify GET /api/meta returns metadata, Class B limits, sensitivity, and 'not covered' list."""
    response = client.get("/api/meta")
    assert response.status_code == 200
    data = response.json()

    assert "limits_used" in data
    assert "Dissolved oxygen" in data["limits_used"]
    assert "sensitivity_analysis" in data
    assert "stability_statement" in data
    assert "what_this_tool_does_not_cover" in data
    assert len(data["what_this_tool_does_not_cover"]) > 0
    assert "data_gaps" in data
    assert len(data["data_gaps"]) > 0
