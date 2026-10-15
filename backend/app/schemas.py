from enum import StrEnum

from datetime import datetime

from pydantic import BaseModel, Field


class SignLanguage(StrEnum):
    ASL = "ASL"
    SLSL = "SLSL"


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str


class VoiceToSignRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2_000, examples=["Hello, how are you?"])
    sign_language: SignLanguage = Field(default=SignLanguage.ASL)


class VoiceToSignResponse(BaseModel):
    status: str = Field(examples=["mock"])
    source_text: str
    sign_language: SignLanguage
    sign_sequence: list[str]
    message: str


class SignToVoiceRequest(BaseModel):
    sign_sequence: list[str] = Field(
        min_length=1,
        max_length=100,
        examples=[["HELLO", "HOW", "ARE", "YOU"]],
    )
    sign_language: SignLanguage = Field(default=SignLanguage.ASL)


class SignToVoiceResponse(BaseModel):
    status: str = Field(examples=["mock"])
    sign_language: SignLanguage
    recognized_signs: list[str]
    generated_text: str
    audio_available: bool
    message: str


class SignRecognitionResponse(BaseModel):
    status: str = Field(examples=["mock"])
    sign_language: SignLanguage
    sign_sequence: list[str]
    generated_text: str
    message: str
    filename: str
    content_type: str


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120, examples=["First conversation"])
    sign_language: SignLanguage = SignLanguage.ASL


class MessageCreate(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=10_000)


class MessageResponse(MessageCreate):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(ConversationCreate):
    id: str
    created_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    id: str
    title: str
    sign_language: SignLanguage
    created_at: datetime
    message_count: int

    model_config = {"from_attributes": True}
