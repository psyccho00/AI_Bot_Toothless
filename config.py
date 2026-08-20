import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Toothless - AI Health Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./toothless.db"  # SQLite for easy local development
    )
    
    # Claude API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-opus-4-20250805"
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-3.5-flash"
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    
    # AI Provider routing selection
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto")  # 'auto', 'anthropic', 'gemini', 'groq'
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Emergency & Medical Panel Settings
    EMERGENCY_PHONE_DEFAULT: str = os.getenv("EMERGENCY_PHONE_DEFAULT", "112")
    MAPS_API_KEY: str = os.getenv("MAPS_API_KEY", "")
    ROUTING_API_KEY: str = os.getenv("ROUTING_API_KEY", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

