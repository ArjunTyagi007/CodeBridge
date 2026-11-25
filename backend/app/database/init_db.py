
from app.database.connection import engine, Base

# Import models so SQLAlchemy knows which tables to create
from app.models.translation import TranslationHistory

# Create all registered database tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
