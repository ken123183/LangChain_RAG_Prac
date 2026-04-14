"""
config.py
專案的全域設定檔。
使用 Pydantic BaseSettings 來管理環境變數與系統常數 (例如 API 路徑、ChromaDB 儲存位置)。
讓專案其他部分能夠統一且安全地存取環境設定。
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Langchain RAG API"
    API_V1_STR: str = "/api/v1"
    
    # Optional default API key, but we mainly expect it from the frontend client request
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # ChromaDB Settings (使用 /tmp 以確保在雲端環境具備寫入權限)
    CHROMA_PERSIST_DIRECTORY: str = "/tmp/chroma_db"
    
    # Security Settings
    DEMO_PASSWORD: str = os.getenv("DEMO_PASSWORD", "123456")
    
    class Config:
        env_file = ".env"

settings = Settings()
