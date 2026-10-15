from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, Message
from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationSummary,
    MessageCreate,
    MessageResponse,
    SignToVoiceRequest,
    SignToVoiceResponse,
    SignLanguage,
    SignRecognitionResponse,
    VoiceToSignRequest,
    VoiceToSignResponse,
)
from app.services import translate_sign_to_voice, translate_voice_to_sign
from app.recognition import recognize_sign_image


router = APIRouter(prefix="/api/v1", tags=["translation"])


@router.post("/voice-to-sign", response_model=VoiceToSignResponse)
def voice_to_sign(request: VoiceToSignRequest) -> VoiceToSignResponse:
    return translate_voice_to_sign(request)


@router.post("/sign-to-voice", response_model=SignToVoiceResponse)
def sign_to_voice(request: SignToVoiceRequest) -> SignToVoiceResponse:
    return translate_sign_to_voice(request)


@router.post("/sign-to-voice/image", response_model=SignRecognitionResponse)
async def sign_to_voice_image(
    image: UploadFile = File(...),
    sign_language: SignLanguage = Form(SignLanguage.ASL),
) -> SignRecognitionResponse:
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    return await recognize_sign_image(image, sign_language)


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    request: ConversationCreate, db: Session = Depends(get_db)
) -> Conversation:
    conversation = Conversation(
        title=request.title,
        sign_language=request.sign_language.value,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(db: Session = Depends(get_db)) -> list[Conversation]:
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_message(
    conversation_id: str,
    request: MessageCreate,
    db: Session = Depends(get_db),
) -> Message:
    if db.get(Conversation, conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = Message(conversation_id=conversation_id, **request.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)) -> None:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()
