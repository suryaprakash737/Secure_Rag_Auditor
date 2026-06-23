from fastapi.testclient import TestClient

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
