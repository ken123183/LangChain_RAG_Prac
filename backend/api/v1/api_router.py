"""
api_router.py
API 路由的中央集線器。
負責將分散在各個模組 (例如 documents, chat) 的路徑匯集並統一註冊到 FastAPI 實例上。
"""
from fastapi import APIRouter
from api.v1.endpoints import documents, chat, auth

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
