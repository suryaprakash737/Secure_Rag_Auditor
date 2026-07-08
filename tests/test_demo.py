from fastapi.testclient import TestClient

from app.api.routes import demo
from app.api.routes.demo import demo_page
from app.main import app


client = TestClient(app)


def test_get_demo_returns_200():
    response = client.get("/demo")

    assert response.status_code == 200


def test_demo_page_renders():
    response = client.get("/demo")

    assert "Secure RAG Auditor Demo" in response.text
    assert "show failed login attempts" in response.text
    assert "Failed Login Attempts" in response.text


def test_demo_route_callable():
    assert callable(demo_page)


def test_demo_analyze_disabled_when_enable_demo_false(monkeypatch):
    monkeypatch.setattr(demo.settings, "ENABLE_DEMO", False)

    response = client.post("/demo/analyze", json={"query": "show failed login attempts"})

    assert response.status_code == 404
