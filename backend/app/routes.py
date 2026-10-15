from fastapi import APIRouter

from app.schemas import VoiceToSignRequest, VoiceToSignResponse
from app.services import translate_voice_to_sign


router = APIRouter(prefix="/api/v1", tags=["translation"])


@router.post("/voice-to-sign", response_model=VoiceToSignResponse)
def voice_to_sign(request: VoiceToSignRequest) -> VoiceToSignResponse:
    return translate_voice_to_sign(request)
