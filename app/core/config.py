from pydantic_settings import BaseSettings
from pydantic import (
    Field
)

class Settings(BaseSettings):
    PROJECT_NAME: str  = "Walt assistant"
    VERSION: str = "1.0.0"
    VECTOR_DATABASE_URL: str = "chroma.db"
    EMBEDDING_DIMENSION: int = 128
    OPENAI_API_KEY: str = "sk-1234567890"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    MODEL_NAME: str 
    CLEANUP_INTERVAL_MINUTES: int = 10
    SESSION_TIMEOUT_MINUTES: int = 10
    AUTH_TOKEN: str
    
    class Config:
        env_file = ".env"

settings = Settings()