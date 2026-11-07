import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_without_api_key(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "local"}


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
def test_local_cors(monkeypatch, origin):
    monkeypatch.delenv("UNHEARD_CORS_ORIGINS", raising=False)
    response = TestClient(create_app()).options(
        "/health", headers={"Origin": origin, "Access-Control-Request-Method": "GET"}
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_foreign_origin_not_allowed():
    response = TestClient(create_app()).get("/health", headers={"Origin": "https://example.com"})
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("origin", ["*", "https://example.com", "http://localhost:5173/path"])
def test_unsafe_cors_configuration_rejected(monkeypatch, origin):
    monkeypatch.setenv("UNHEARD_CORS_ORIGINS", origin)
    with pytest.raises(ValueError):
        create_app()


def test_custom_local_port(monkeypatch):
    monkeypatch.setenv("UNHEARD_CORS_ORIGINS", "http://localhost:5174")
    response = TestClient(create_app()).get("/health", headers={"Origin": "http://localhost:5174"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5174"
