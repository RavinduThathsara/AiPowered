from fastapi.testclient import TestClient

from app.main import app
from app.schemas import SignLanguage


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "signbridge-api"}


def test_unknown_route_returns_not_found() -> None:
    response = client.get("/api/v1/unknown")

    assert response.status_code == 404


def test_health_response_has_openapi_schema() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["components"]["schemas"]["HealthResponse"]["required"] == [
        "status",
        "service",
    ]


def test_supported_sign_languages_are_explicit() -> None:
    assert [language.value for language in SignLanguage] == ["ASL", "SLSL"]


def test_voice_to_sign_returns_mock_sign_sequence() -> None:
    response = client.post(
        "/api/v1/voice-to-sign",
        json={"text": "Hello, how are you?", "sign_language": "ASL"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "mock"
    assert response.json()["sign_sequence"] == ["HELLO", "HOW", "ARE", "YOU"]
    assert response.json()["sign_language"] == "ASL"


def test_voice_to_sign_rejects_empty_text() -> None:
    response = client.post(
        "/api/v1/voice-to-sign",
        json={"text": "", "sign_language": "SLSL"},
    )

    assert response.status_code == 422
