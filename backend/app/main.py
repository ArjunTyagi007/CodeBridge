
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CodeBridge API",
    description="AI-powered Programming Language Translator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to CodeBridge!",
        "status": "Backend is running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
