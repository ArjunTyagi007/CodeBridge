
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.translator.python_to_js import translate_python_to_js

router = APIRouter()


class TranslationRequest(BaseModel):
    source_language: str
    target_language: str
    code: str


@router.post("/translate")
def translate_code(request: TranslationRequest):

    try:
        if (
            request.source_language.lower() == "python"
            and request.target_language.lower() == "javascript"
        ):
            translated_code = translate_python_to_js(request.code)

        else:
            raise HTTPException(
                status_code=400,
                detail="This language combination is not supported yet."
            )

        return {
            "message": "Translation successful!",
            "source_language": request.source_language,
            "target_language": request.target_language,
            "original_code": request.code,
            "translated_code": translated_code
        }

    except SyntaxError as error:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Python syntax: {error}"
        )

    except NotImplementedError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
