import re

from app.schemas import (
    SignToVoiceRequest,
    SignToVoiceResponse,
    VoiceToSignRequest,
    VoiceToSignResponse,
)


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


def translate_sign_to_voice(request: SignToVoiceRequest) -> SignToVoiceResponse:
    recognized_signs = [sign.strip().upper() for sign in request.sign_sequence]

    return SignToVoiceResponse(
        status="mock",
        sign_language=request.sign_language,
        recognized_signs=recognized_signs,
        generated_text=" ".join(recognized_signs).capitalize(),
        audio_available=False,
        message=(
            "Mock output only. Connect a sign-recognition and voice-generation "
            "provider to produce real audio."
        ),
    )
