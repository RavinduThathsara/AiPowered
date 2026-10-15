from enum import StrEnum

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
