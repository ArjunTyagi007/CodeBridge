
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db
from app.models.translation import TranslationHistory

from app.translator.python_to_js import translate_python_to_js
from app.translator.javascript_to_python import (
    translate_javascript_to_python
)

router = APIRouter()


class TranslationRequest(BaseModel):
    source_language: str
    target_language: str
    code: str


@router.post("/translate")
def translate_code(
    request: TranslationRequest,
    db: Session = Depends(get_db)
):

    source = request.source_language.lower()
    target = request.target_language.lower()

    if not request.code.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter code to translate."
        )

    try:

        # Python to JavaScript
        if source == "python" and target == "javascript":
            translated_code = translate_python_to_js(
                request.code
            )

        # JavaScript to Python
        elif source == "javascript" and target == "python":
            translated_code = translate_javascript_to_python(
                request.code
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="This language combination is not supported yet."
            )

        # Save translation in PostgreSQL
        history = TranslationHistory(
            source_language=source,
            target_language=target,
            original_code=request.code,
            translated_code=translated_code
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "message": "Translation successful and saved!",
            "history_id": history.id,
            "source_language": source,
            "target_language": target,
            "original_code": request.code,
            "translated_code": translated_code,
            "created_at": history.created_at
        }

    except HTTPException:
        raise

    except (SyntaxError, NotImplementedError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Translation succeeded, but saving to history failed."
        )
