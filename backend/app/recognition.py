from fastapi import UploadFile

from app.schemas import SignLanguage, SignRecognitionResponse


async def recognize_sign_image(
    image: UploadFile, sign_language: SignLanguage
) -> SignRecognitionResponse:
    return SignRecognitionResponse(
        status="mock",
        sign_language=sign_language,
        sign_sequence=["IMAGE_RECEIVED"],
        generated_text="Image received for sign recognition.",
        message=(
            "Mock output only. Connect a computer-vision provider to recognize "
            "sign language from this image."
        ),
        filename=image.filename or "uploaded-image",
        content_type=image.content_type or "application/octet-stream",
    )
