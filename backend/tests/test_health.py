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


def test_sign_to_voice_returns_mock_text() -> None:
    response = client.post(
        "/api/v1/sign-to-voice",
        json={
            "sign_sequence": ["HELLO", "HOW", "ARE", "YOU"],
            "sign_language": "SLSL",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "mock"
    assert response.json()["recognized_signs"] == ["HELLO", "HOW", "ARE", "YOU"]
    assert response.json()["generated_text"] == "Hello how are you"
    assert response.json()["audio_available"] is False


def test_sign_to_voice_rejects_empty_sequence() -> None:
    response = client.post(
        "/api/v1/sign-to-voice",
        json={"sign_sequence": [], "sign_language": "ASL"},
    )

    assert response.status_code == 422


def test_sign_image_endpoint_returns_mock_recognition() -> None:
    response = client.post(
        "/api/v1/sign-to-voice/image",
        files={"image": ("sign.png", b"fake-image", "image/png")},
        data={"sign_language": "ASL"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "mock"
    assert response.json()["sign_sequence"] == ["IMAGE_RECEIVED"]
    assert response.json()["filename"] == "sign.png"


def test_sign_image_endpoint_rejects_non_image_uploads() -> None:
    response = client.post(
        "/api/v1/sign-to-voice/image",
        files={"image": ("notes.txt", b"not-an-image", "text/plain")},
    )

    assert response.status_code == 415


def test_conversation_messages_can_be_saved_and_retrieved() -> None:
    conversation_response = client.post(
        "/api/v1/conversations",
        json={"title": "Test conversation", "sign_language": "ASL"},
    )

    assert conversation_response.status_code == 201
    conversation = conversation_response.json()
    conversation_id = conversation["id"]

    message_response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello"},
    )

    assert message_response.status_code == 201
    assert message_response.json()["content"] == "Hello"

    retrieved = client.get(f"/api/v1/conversations/{conversation_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["messages"][0]["content"] == "Hello"


def test_message_for_unknown_conversation_returns_not_found() -> None:
    response = client.post(
        "/api/v1/conversations/does-not-exist/messages",
        json={"role": "user", "content": "Hello"},
    )

    assert response.status_code == 404


def test_conversations_can_be_listed_with_message_count() -> None:
    conversation_response = client.post(
        "/api/v1/conversations",
        json={"title": "List me", "sign_language": "ASL"},
    )
    conversation_id = conversation_response.json()["id"]
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "Welcome"},
    )

    response = client.get("/api/v1/conversations")

    assert response.status_code == 200
    listed = next(item for item in response.json() if item["id"] == conversation_id)
    assert listed["message_count"] == 1


def test_conversation_can_be_deleted_with_its_messages() -> None:
    conversation_response = client.post(
        "/api/v1/conversations",
        json={"title": "Delete me", "sign_language": "SLSL"},
    )
    conversation_id = conversation_response.json()["id"]
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Remove this"},
    )

    delete_response = client.delete(f"/api/v1/conversations/{conversation_id}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/conversations/{conversation_id}").status_code == 404


def test_deleting_unknown_conversation_returns_not_found() -> None:
    response = client.delete("/api/v1/conversations/does-not-exist")

    assert response.status_code == 404
