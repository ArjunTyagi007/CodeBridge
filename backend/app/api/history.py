
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.translation import TranslationHistory

router = APIRouter()


# Get all translation history
@router.get("/history")
def get_translation_history(
    db: Session = Depends(get_db)
):
    history = (
        db.query(TranslationHistory)
        .order_by(TranslationHistory.created_at.desc())
        .all()
    )

    return history


# Get one translation by ID
@router.get("/history/{history_id}")
def get_translation_by_id(
    history_id: int,
    db: Session = Depends(get_db)
):

    history = (
        db.query(TranslationHistory)
        .filter(TranslationHistory.id == history_id)
        .first()
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Translation history not found."
        )

    return history
