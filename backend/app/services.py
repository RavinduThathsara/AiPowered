import re

from app.schemas import VoiceToSignRequest, VoiceToSignResponse


def translate_voice_to_sign(request: VoiceToSignRequest) -> VoiceToSignResponse:
    words = re.findall(r"[A-Za-z0-9']+", request.text)

    return VoiceToSignResponse(
        status="mock",
        source_text=request.text,
        sign_language=request.sign_language,
        sign_sequence=[word.upper() for word in words],
        message=(
            "Mock output only. Connect a speech and sign-translation provider "
            "to generate real sign language output."
        ),
    )
