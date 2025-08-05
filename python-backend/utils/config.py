"""
Configuration settings for the Insurance AI Backend
"""

import os
from typing import Optional
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"

        # API Configuration
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GLM_API_KEY = os.getenv("GLM_API_KEY")
        self.GLM_API_URL = os.getenv("GLM_API_URL", "https://open.bigmodel.cn/api/paas/v4/")

        # Gemini API Configuration (for multi-AI processing)
        self.GEMINI_API_KEYS = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5"),
        ]
        # Filter out None values
        self.GEMINI_API_KEYS = [key for key in self.GEMINI_API_KEYS if key]
        self.GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent")

        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./insurance_ai.db")

        # File Upload Configuration
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
        self.UPLOAD_PATH = os.getenv("UPLOAD_PATH", "./uploads")
        self.PROCESSED_DOCUMENTS_PATH = os.getenv("PROCESSED_DOCUMENTS_PATH", "./processed_documents")

        # AI Configuration
        self.AI_RESPONSE_TIMEOUT = int(os.getenv("AI_RESPONSE_TIMEOUT", "30"))  # 30 seconds
        self.TARGET_RESPONSE_TIME = float(os.getenv("TARGET_RESPONSE_TIME", "0.03"))  # 30ms

        # Security Configuration
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

        # Analytics
        self.ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "90"))

        # Document Processing
        self.TESSERACT_PATH = os.getenv("TESSERACT_PATH")
        self.POPPLER_PATH = os.getenv("POPPLER_PATH")

        # Supported file types
        self.SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "tiff", "bmp", "gif"]
        self.SUPPORTED_DOCUMENT_TYPES = ["pdf", "docx", "doc", "txt"]

# Create settings instance
settings = Settings()

# Validate critical settings
def validate_settings():
    """Validate critical configuration settings"""
    errors = []
    
    if not settings.GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required")
    
    if not os.path.exists(settings.UPLOAD_PATH):
        try:
            os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create upload directory: {e}")
    
    if not os.path.exists(settings.PROCESSED_DOCUMENTS_PATH):
        try:
            os.makedirs(settings.PROCESSED_DOCUMENTS_PATH, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create processed documents directory: {e}")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

# Validate on import
validate_settings()
