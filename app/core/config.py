from pydantic import BaseSettings
from pydantic import (
    Field
)

class Settings(BaseSettings):
    PROJECT_NAME: str  = Field(default="Walt assistant")
    VERSION: str = Field(default="0.0.1")
    VECTOR_DATABASE_URL: str = Field(default="chroma.db")
    EMBEDDING_DIMENSION: int = Field(default=128)
    OPENAI_API_KEY: str = Field(default="sk-1234567890")
    EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002")
    
    
    class Config:
        env_file = ".env"

settings = Settings()