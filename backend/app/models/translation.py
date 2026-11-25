
from sqlalchemy import Column, Integer, String, Text, DateTime, func

from app.database.connection import Base


class TranslationHistory(Base):
    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)

    source_language = Column(String(50), nullable=False)
    target_language = Column(String(50), nullable=False)

    original_code = Column(Text, nullable=False)
    translated_code = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
