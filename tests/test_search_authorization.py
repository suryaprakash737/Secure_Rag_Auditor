from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.main import app
from app.models.user import User


client = TestClient(app)


def _user(clearance_level: int) -> User:
    return User(
        username=f"clearance-{clearance_level}",
        hashed_password="hashed",
        role="analyst",
        clearance_level=clearance_level,
        is_active=True,
    )


def _retrieval_results():
    return {
        "documents": [
            [
                "Low security failed login from 10.0.0.1",
                "High security classified incident from 10.0.0.9",
            ]
        ],
        "metadatas": [
            [
                {"source_device": "low-sensor", "security_level": 1},
                {"source_device": "high-sensor", "security_level": 5},
            ]
        ],
    }


def _install_search_mocks(monkeypatch):
    from app.api.routes import search

    captured = {}

    def fake_secure_retrieval(query_text, user_clearance):
        captured["retrieval_clearance"] = user_clearance
        return _retrieval_results()

    async def fake_generate_security_summary(query, docs, meta, threat_intel_findings=None):
        captured["llm_docs"] = docs
        captured["llm_meta"] = meta
        return {
            "summary": "Authorized analysis",
            "risk_level": "Low",
            "key_findings": docs,
            "recommendation": "Review authorized logs.",
        }

    def fake_log_search(*args, **kwargs):
        captured["audit_args"] = args

    monkeypatch.setattr(search, "secure_retrieval", fake_secure_retrieval)
    monkeypatch.setattr(search, "generate_security_summary", fake_generate_security_summary)
    monkeypatch.setattr(search, "log_search", fake_log_search)
    return captured


def teardown_function():
    app.dependency_overrides.clear()


def test_unauthenticated_search_returns_401():
    response = client.post("/search", json={"query": "show failed login attempts"})

    assert response.status_code == 401


def test_authenticated_low_clearance_user_cannot_retrieve_high_security_documents(monkeypatch):
    captured = _install_search_mocks(monkeypatch)
    app.dependency_overrides[get_current_user] = lambda: _user(clearance_level=1)

    response = client.post("/search", json={"query": "show failed login attempts"})

    assert response.status_code == 200
    assert response.json()["sources"] == [{"source_device": "low-sensor", "security_level": 1}]
    assert captured["llm_docs"] == ["Low security failed login from 10.0.0.1"]


def test_authenticated_high_clearance_user_can_retrieve_permitted_documents(monkeypatch):
    captured = _install_search_mocks(monkeypatch)
    app.dependency_overrides[get_current_user] = lambda: _user(clearance_level=5)

    response = client.post("/search", json={"query": "show failed login attempts"})

    assert response.status_code == 200
    assert response.json()["log_count"] == 2
    assert captured["llm_docs"] == [
        "Low security failed login from 10.0.0.1",
        "High security classified incident from 10.0.0.9",
    ]


def test_request_body_cannot_override_user_clearance(monkeypatch):
    captured = _install_search_mocks(monkeypatch)
    app.dependency_overrides[get_current_user] = lambda: _user(clearance_level=1)

    response = client.post(
        "/search",
        json={"query": "show failed login attempts", "clearance_level": 999},
    )

    assert response.status_code == 422
    assert "retrieval_clearance" not in captured


def test_llm_prompt_only_receives_authorized_retrieved_documents(monkeypatch):
    captured = _install_search_mocks(monkeypatch)
    app.dependency_overrides[get_current_user] = lambda: _user(clearance_level=1)

    response = client.post("/search", json={"query": "show failed login attempts"})

    assert response.status_code == 200
    assert captured["llm_docs"] == ["Low security failed login from 10.0.0.1"]
    assert captured["llm_meta"] == [{"source_device": "low-sensor", "security_level": 1}]
