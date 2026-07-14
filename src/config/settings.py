import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 200
    
    TOP_K: int = 5
    SCORE_THRESHOLD: float = 0.65
    
    CHROMA_PERSIST_DIR: str = "./data/vectorstore"
    CHROMA_COLLECTION: str = "mutual_fund_faq"
    
    class Config:
        env_file = ".env"

settings = Settings()
