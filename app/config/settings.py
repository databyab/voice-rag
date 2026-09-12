from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = Field(default="groq/compound")
    
    CHROMA_PATH: str = Field(default=str(BASE_DIR / "data" / "chroma"))
    DOCUMENTS_DIR: str = Field(default=str(BASE_DIR / "data" / "documents"))
    
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    
    RAG_TOP_K: int = Field(default=5)
    CHUNK_SIZE: int = Field(default=800)
    CHUNK_OVERLAP: int = Field(default=150)
    
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

settings = Settings()

