import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.routes import demo
from app.core.rate_limit import RateLimiter, login_limiter
from app.main import app
from app.services import llm_service


client = TestClient(app)


# --- Rate limiting -----------------------------------------------------------

def test_rate_limiter_blocks_after_limit():
    limiter = RateLimiter(max_requests=2, window_seconds=60, name="test")
    limiter.check("1.2.3.4")
    limiter.check("1.2.3.4")

    with pytest.raises(HTTPException) as exc_info:
        limiter.check("1.2.3.4")

    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers


def test_rate_limiter_tracks_clients_separately():
    limiter = RateLimiter(max_requests=1, window_seconds=60, name="test")
    limiter.check("1.1.1.1")
    limiter.check("2.2.2.2")  # different client, not limited


def test_login_endpoint_is_rate_limited(monkeypatch):
    # Exhaust the limiter for the test client's IP, then the route must refuse
    # before touching the database.
    for _ in range(login_limiter.max_requests):
        login_limiter.check("testclient")

    response = client.post("/login", json={"username": "x", "password": "y"})

    assert response.status_code == 429


# --- Demo hardening ----------------------------------------------------------

def test_demo_clearance_is_below_admin():
    assert demo.DEMO_CLEARANCE_LEVEL < 4


def test_demo_analyze_uses_demo_clearance_and_is_audited(monkeypatch):
    captured = {}

    def fake_analyze_incident(query, clearance_level):
        captured["clearance"] = clearance_level
        return {"risk_level": "Low", "log_count": 1, "was_blocked": False}

    def fake_log_search(query, clearance, risk_level, log_count, was_blocked):
        captured["audit"] = (query, clearance, risk_level, log_count, was_blocked)

    monkeypatch.setattr(demo.settings, "ENABLE_DEMO", True)
    monkeypatch.setattr(demo, "analyze_incident", fake_analyze_incident)
    monkeypatch.setattr(demo, "log_search", fake_log_search)

    response = client.post("/demo/analyze", json={"query": "show failed login attempts"})

    assert response.status_code == 200
    assert captured["clearance"] == demo.DEMO_CLEARANCE_LEVEL
    assert captured["audit"] == (
        "show failed login attempts", demo.DEMO_CLEARANCE_LEVEL, "Low", 1, False
    )


def test_demo_rejects_oversized_query(monkeypatch):
    monkeypatch.setattr(demo.settings, "ENABLE_DEMO", True)

    response = client.post("/demo/analyze", json={"query": "a" * 501})

    assert response.status_code == 422


# --- LLM service -------------------------------------------------------------

def test_groq_model_is_configurable(monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    assert llm_service._get_model() == llm_service.DEFAULT_GROQ_MODEL

    monkeypatch.setenv("GROQ_MODEL", "some/other-model")
    assert llm_service._get_model() == "some/other-model"


def test_llm_failure_does_not_leak_provider_error(monkeypatch):
    class ExplodingClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    raise RuntimeError("secret-internal-detail model_not_found")

    monkeypatch.setattr(llm_service, "_get_client", lambda: ExplodingClient)

    result = asyncio.run(
        llm_service.generate_security_summary("q", ["log"], [{"security_level": 1}])
    )

    assert result["risk_level"] == "Unknown"
    assert "secret-internal-detail" not in result["summary"]
    assert "model_not_found" not in result["summary"]
